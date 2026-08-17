import requests, json, uuid
BASE='https://link-please-assignment.onrender.com'

print('Base URL:', BASE)

# 1) Create rule
try:
    r = requests.post(BASE + '/rules', json={'keyword':'hello','dm_message':'Hi from assistant'}, timeout=15)
    print('\nPOST /rules ->', r.status_code)
    print(r.text)
except Exception as e:
    print('POST /rules error', e)

# 2) GET rules
try:
    r = requests.get(BASE + '/rules', timeout=15)
    print('\nGET /rules ->', r.status_code)
    print(r.text)
except Exception as e:
    print('GET /rules error', e)

# 3) Send webhook (comment.created)
event = {
    'event_id': str(uuid.uuid4()),
    'type': 'comment.created',
    'data': {
        'comment_id': 'c-assist-1',
        'user': {'id': 'user-assist-1'},
        'body': 'hello world'
    }
}
try:
    r = requests.post(BASE + '/webhook', json=event, timeout=15)
    print('\nPOST /webhook ->', r.status_code)
    print(r.text)
except Exception as e:
    print('POST /webhook error', e)

# 4) GET stats
try:
    r = requests.get(BASE + '/stats', timeout=15)
    print('\nGET /stats ->', r.status_code)
    print(r.text)
except Exception as e:
    print('GET /stats error', e)
