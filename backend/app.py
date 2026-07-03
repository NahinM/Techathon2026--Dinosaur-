import os
from flask import Flask, jsonify, request
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DEVICES_TABLE = os.environ.get("SUPABASE_DEVICES_TABLE", "devices")

def get_supabase_client() -> Client | None:
    supabase_url = os.environ.get("SUPABASE_URL")
    # Prefer service role key for backend server usage. Fallback to publishable key.
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_PUBLISHABLE_KEY")
    if not supabase_url or not supabase_key:
        return None

    return create_client(supabase_url, supabase_key)


supabase = get_supabase_client()

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# access api

@app.route("/api/devices", methods=["GET"])
def get_devices():
    if supabase is None:
        return jsonify({"error": "Supabase is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY or SUPABASE_PUBLISHABLE_KEY."}), 500

    try:
        response = supabase.table(DEVICES_TABLE).select("*").order("id").execute()
        return jsonify(response.data), 200
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
            result = supabase.table(DEVICES_TABLE).update({"status": normalized_status}).eq("id", device_id).execute()
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
    return jsonify(response_body), status_code

@app.route("/api/stats", methods=["GET"])
def get_stats():
    stats = {
        "total": 0,
        "Dining Room": 0,
        "Work Room 1": 0,
        "Work Room 2": 0,
    }
    room = {
        1: "Dining Room",
        2: "Work Room 1",
        3: "Work Room 2",
    }
    cost =  {
        "fan": 60,
        "light": 15
    }
    if supabase is None:
        return jsonify({"error": "Supabase is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY or SUPABASE_PUBLISHABLE_KEY."}), 500

    try:
        response = supabase.table('devices').select("id,room_id,device_type,status").order("id").execute()
        for device in response.data:
            room_num = device.get("room_id")
            room_name = room.get(room_num, "Unknown Room")
            device_type = device.get("device_type")
            status = device.get("status")
            if status.lower() == "on":
                stats["total"] += cost.get(device_type, 0)
                stats[room_name] += cost.get(device_type, 0)
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)