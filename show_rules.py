import requests, json
r = requests.get('https://link-please-assignment.onrender.com/rules', timeout=20)
print(r.status_code)
try:
    print(json.dumps(r.json(), indent=2))
except Exception:
    print(r.text)
