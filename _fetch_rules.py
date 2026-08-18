import requests
r = requests.get('https://link-please-assignment.onrender.com/rules', timeout=20)
print(r.status_code)
print(r.text)
