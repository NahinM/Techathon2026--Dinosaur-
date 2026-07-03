import requests
import os

office = {
    "Drawing Room": [
        {"id":1, "type":"fan", "status":"off"},
        {"id":2, "type":"fan", "status":"off"},
        {"id":3, "type":"light", "status":"off"},
        {"id":4, "type":"light", "status":"off"},
        {"id":5, "type":"light", "status":"off"},
    ],
    "Work Room 1":[
        {"id":6, "type":"fan", "status":"off"},
        {"id":7, "type":"fan", "status":"off"},
        {"id":8, "type":"light", "status":"off"},
        {"id":9, "type":"light", "status":"off"},
        {"id":10, "type":"light", "status":"off"},
    ],
    "Work Room 2":[
        {"id":11, "type":"fan", "status":"off"},
        {"id":12, "type":"fan", "status":"off"},
        {"id":13, "type":"light", "status":"off"},
        {"id":14, "type":"light", "status":"off"},
        {"id":15, "type":"light", "status":"off"},
    ]
}

def extract_devices(office):
    """
    Extract all devices from an office dictionary.

    Args:
        office (dict): A dictionary where each key is a room name and each value is a list
                       of device dictionaries (each with 'id', 'type', 'status').

    Returns:
        list: A list of dictionaries, each with keys 'id' and 'status'.
    """
    extracted = []
    for room_name, room_devices in office.items():
        for index, device in enumerate(room_devices, start=1):
            extracted.append({
                "id": device["id"],
                "room": room_name,
                "name": f"{device['type'].title()} {index}",
                "type": device["type"],
                "status": device["status"],
            })
    return extracted


api_url = os.environ.get("API_URL", "http://127.0.0.1:5000/api/devices")
headers = {"Content-Type": "application/json"}

try:
    # Post extracted devices to the backend API.
    response = requests.post(api_url, json=extract_devices(office), headers=headers)
    
    # 5. Check if the request was successful
    response.raise_for_status()
    
    # 6. Parse and use the JSON response from the server
    response_data = response.json()
    print("Success! Response from API:")
    print(response_data)

except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
except Exception as err:
    print(f"An error occurred: {err}")