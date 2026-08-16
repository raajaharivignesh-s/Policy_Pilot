import urllib.request
import json
import urllib.error

data = {
    "query": "check my eligibility",
    "conversation_history": [
        {"role": "user", "content": "explain TPS"},
        {"role": "assistant", "content": "The Tamizh Pudhalvan Scheme (TPS) provides..."}
    ]
}

req = urllib.request.Request(
    'http://127.0.0.1:8000/api/v1/query', 
    data=json.dumps(data).encode('utf-8'), 
    headers={'Content-Type': 'application/json'}
)

try:
    response = urllib.request.urlopen(req)
    print(response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"HTTPError: {e.code}")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(f"Error: {e}")
