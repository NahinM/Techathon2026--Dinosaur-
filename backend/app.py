import os
from flask import Flask, jsonify, request
from supabase import create_client, Client
from dotenv import load_dotenv
from flask_socketio import SocketIO, emit
from typing import Any, cast

load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

DEVICES_TABLE = os.environ.get("SUPABASE_DEVICES_TABLE", "devices")
ROOM_NAMES = {
    1: "Drawing Room",
    2: "Work Room 1",
    3: "Work Room 2",
}
DEVICE_POWER = {
    "fan": 60,
    "light": 15,
}


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

def get_supabase_client() -> Client | None:
    supabase_url = os.environ.get("SUPABASE_URL")
    # Prefer service role key for backend server usage. Fallback to publishable key.
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_PUBLISHABLE_KEY")
    if not supabase_url or not supabase_key:
        return None

    return create_client(supabase_url, supabase_key)


supabase = get_supabase_client()


def to_bool(status_value) -> bool:
    if isinstance(status_value, bool):
        return status_value
    if isinstance(status_value, str):
        return status_value.strip().lower() in ("on", "true", "1")
    return bool(status_value)


def normalize_status(status_value) -> str:
    return "on" if to_bool(status_value) else "off"


def calculate_power(device_type: str, status_value) -> int:
    if not to_bool(status_value):
        return 0
    return DEVICE_POWER.get(device_type, 0)


def fetch_devices_from_db():
    if supabase is None:
        raise RuntimeError("Supabase is not configured")

    response = supabase.table(DEVICES_TABLE).select(
        "id,room_id,device_type,status,power_draw,name,last_changed,continuous_on_since"
    ).order("id").execute()
    return cast(list[dict[str, Any]], response.data or [])


def calculate_stats_from_devices(devices):
    stats = {
        "total": 0,
        "Drawing Room": 0,
        "Work Room 1": 0,
        "Work Room 2": 0,
    }

    for device in devices:
        room_name = ROOM_NAMES.get(device.get("room_id"), "Unknown Room")
        power_value = device.get("power_draw") or device.get("power") or 0

        try:
            power_value = int(power_value)
        except (TypeError, ValueError):
            power_value = 0

        stats["total"] += power_value
        if room_name in stats:
            stats[room_name] += power_value

    return stats


def fetch_live_state():
    devices = fetch_devices_from_db()
    return {
        "devices": devices,
        "stats": calculate_stats_from_devices(devices),
    }


def emit_live_state():
    if supabase is None:
        return

    try:
        socketio.emit("state_update", fetch_live_state())
    except Exception:
        pass

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# access api

@app.route("/api/devices", methods=["GET"])
def get_devices():
    if supabase is None:
        return jsonify({"error": "Supabase is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY or SUPABASE_PUBLISHABLE_KEY."}), 500

    try:
        return jsonify(fetch_devices_from_db()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/devices", methods=["POST"])
def post_devices():
    if supabase is None:
        return jsonify({"error": "Supabase is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY or SUPABASE_PUBLISHABLE_KEY."}), 500

    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "Invalid JSON body"}), 400

    records = payload if isinstance(payload, list) else [payload]
    if not records:
        return jsonify({"error": "No device records provided"}), 400

    updated_records = []
    missing_ids = []
    failed_updates = []

    for record in records:
        device_id = record.get("id")
        if device_id is None:
            return jsonify({"error": "Each record must include an 'id' field"}), 400

        raw_status = record.get("status")
        if raw_status is None:
            return jsonify({"error": f"Record with id {device_id} must include a 'status' field"}), 400

        if isinstance(raw_status, str):
            status_value = raw_status.strip().lower()
            if status_value in ("on", "true", "1"):
                normalized_status = "on"
            elif status_value in ("off", "false", "0"):
                normalized_status = "off"
            else:
                return jsonify({"error": f"Unsupported status value for id {device_id}: {raw_status}"}), 400
        else:
            normalized_status = "on" if bool(raw_status) else "off"

        try:
            existing_result = supabase.table(DEVICES_TABLE).select("id,device_type").eq("id", device_id).limit(1).execute()
            existing_rows = cast(list[dict[str, Any]], existing_result.data or [])
            if not existing_rows:
                missing_ids.append(device_id)
                continue

            device_type = str(existing_rows[0].get("device_type", ""))
            update_payload = {
                "status": normalized_status,
                "power_draw": calculate_power(device_type, normalized_status),
            }

            result = (
                supabase.table(DEVICES_TABLE)
                .update(update_payload)
                .eq("id", device_id)
                .select(
                    "id,room_id,device_type,status,power_draw,name,last_changed,continuous_on_since"
                )
                .execute()
            )
        except Exception as exc:
            failed_updates.append({"id": device_id, "error": str(exc)})
            continue

        if not result.data:
            missing_ids.append(device_id)
            continue

        updated_records.extend(result.data)

    response_body = {
        "updated_count": len(updated_records),
        "updated": updated_records,
    }

    if missing_ids:
        response_body["missing_ids"] = missing_ids

    if failed_updates:
        response_body["failed_updates"] = failed_updates

    status_code = 200 if not failed_updates else 207
    emit_live_state()
    return jsonify(response_body), status_code

@app.route("/api/stats", methods=["GET"])
def get_stats():
    if supabase is None:
        return jsonify({"error": "Supabase is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY or SUPABASE_PUBLISHABLE_KEY."}), 500

    try:
        devices = fetch_devices_from_db()
        return jsonify(calculate_stats_from_devices(devices)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@socketio.on("connect")
def handle_connect():
    if supabase is None:
        emit("state_update", {"error": "Supabase is not configured"})
        return

    try:
        emit("state_update", fetch_live_state())
    except Exception as exc:
        emit("state_update", {"error": str(exc)})
    

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)