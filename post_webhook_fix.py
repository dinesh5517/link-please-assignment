import requests, uuid
BASE='https://link-please-assignment.onrender.com'

event = {
    'event_id': str(uuid.uuid4()),
    'event_type': 'comment.created',
    'data': {
        'comment_id': 'c-assist-2',
        'from': {'user_id': 'user-assist-1'},
        'text': 'hello world'
    }
}
try:
    r = requests.post(BASE + '/webhook', json=event, timeout=15)
    print('POST /webhook ->', r.status_code)
    print(r.text)
except Exception as e:
    print('POST /webhook error', e)

# fetch stats
try:
    r = requests.get(BASE + '/stats', timeout=15)
    print('\nGET /stats ->', r.status_code)
    print(r.text)
except Exception as e:
    print('GET /stats error', e)
