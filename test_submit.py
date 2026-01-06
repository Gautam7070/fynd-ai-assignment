import requests
import json

url = "http://127.0.0.1:8001/submit-review"
payload = {"rating": 5, "review": "This is a great test review."}
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
