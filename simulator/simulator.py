import requests

office = {
    "Drawing Room: 1": [
        {"id":1, "type":"fan", "status":"on"},
        {"id":2, "type":"fan", "status":"on"},
        {"id":3, "type":"light", "status":"on"},
        {"id":4, "type":"light", "status":"on"},
        {"id":5, "type":"light", "status":"on"},
    ],
    "Work Room 1":[
        {"id":6, "type":"fan", "status":"on"},
        {"id":7, "type":"fan", "status":"on"},
        {"id":8, "type":"light", "status":"on"},
        {"id":9, "type":"light", "status":"on"},
        {"id":10, "type":"light", "status":"on"},
    ],
    "Work Room 2":[
        {"id":11, "type":"fan", "status":"on"},
        {"id":12, "type":"fan", "status":"on"},
        {"id":13, "type":"light", "status":"on"},
        {"id":14, "type":"light", "status":"on"},
        {"id":15, "type":"light", "status":"on"},
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
    return [
        {"id": device["id"], "status": device["status"]}
        for room_devices in office.values()
        for device in room_devices
    ]


api_url = "https://httpbin.org/post"
headers = {
    "Authorization": "Bearer YOUR_ACCESS_TOKEN"
}

try:
    # 4. Execute the POST request using the json= parameter
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