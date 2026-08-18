import os
import hmac
import hashlib
import json
import time
import requests
from uuid import uuid4

WEBHOOK_URL='https://link-please-assignment.onrender.com/webhook'
EVENTS_URL='https://link-please-assignment.onrender.com/events'
JOBS_URL='https://link-please-assignment.onrender.com/jobs'
STATS_URL='https://link-please-assignment.onrender.com/stats'

# read key from .env in the same folder
def read_key():
    path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(path):
        with open(path,'r', encoding='utf-8') as f:
            for l in f:
                if l.strip().startswith('PSEUDOGRAM_API_KEY='):
                    return l.split('=',1)[1].strip()
    env = os.getenv('PSEUDOGRAM_API_KEY')
    return env

KEY = read_key()
if not KEY:
    print('PSEUDOGRAM_API_KEY not found in .env or env')
    raise SystemExit(2)

headers_base = {'Content-Type':'application/json'}

def sign_and_post(payload):
    body = json.dumps(payload, separators=(',',':')).encode()
    sig = hmac.new(KEY.encode(), body, hashlib.sha256).hexdigest()
    headers = dict(headers_base)
    headers['X-PseudoGram-Signature'] = 'sha256=' + sig
    r = requests.post(WEBHOOK_URL, data=body, headers=headers, timeout=30)
    print('POST', payload.get('event_type'), '->', r.status_code, r.text)
    return r


def ensure_price_rule():
    try:
        r = requests.get('https://link-please-assignment.onrender.com/rules', timeout=30)
        if r.status_code == 200:
            rules = r.json()
            for ru in rules:
                if ru.get('keyword','').lower() == 'price':
                    print('PRICE rule already exists on deployed service')
                    return True
        # create rule
        payload = {'keyword':'PRICE','dm_message':'Thanks for asking about PRICE — here is info.'}
        r = requests.post('https://link-please-assignment.onrender.com/rules', json=payload, timeout=30)
        print('Create PRICE rule ->', r.status_code, r.text)
        return r.status_code in (200,201)
    except Exception as e:
        print('Error ensuring PRICE rule', e)
        return False

# create events
user1 = 'usr_test_1'
user2 = 'usr_test_2'

c1 = 'c_test_1'
c2 = 'c_test_2'

# 1) comment.created matching rule (PRICE) -> should create job
evt1 = {
    'event_id': f'evt_{uuid4().hex[:8]}',
    'event_type': 'comment.created',
    'sent_at': '2026-08-17T00:00:00Z',
    'data': {
        'comment_id': c1,
        'post_id': 'pst_test',
        'text': 'PRICE check please',
        'created_at': '2026-08-17T00:00:00Z',
        'from': {'user_id': user1}
    }
}

# 2) comment.accepted matching rule -> should create job
evt2 = {
    'event_id': f'evt_{uuid4().hex[:8]}',
    'event_type': 'comment.accepted',
    'sent_at': '2026-08-17T00:00:01Z',
    'data': {
        'comment_id': c2,
        'post_id': 'pst_test',
        'text': 'Can I see the PRICE list',
        'created_at': '2026-08-17T00:00:01Z',
        'from': {'user_id': user2}
    }
}

# 3) comment.deleted for c1 -> should cancel queued job if any
evt3 = {
    'event_id': f'evt_{uuid4().hex[:8]}',
    'event_type': 'comment.deleted',
    'sent_at': '2026-08-17T00:00:02Z',
    'data': {
        'comment_id': c1
    }
}

# 4) non-matching created (should be ignored)
evt4 = {
    'event_id': f'evt_{uuid4().hex[:8]}',
    'event_type': 'comment.created',
    'sent_at': '2026-08-17T00:00:03Z',
    'data': {
        'comment_id': 'c_test_3',
        'post_id': 'pst_test',
        'text': 'hello world',
        'created_at': '2026-08-17T00:00:03Z',
        'from': {'user_id': 'usr_test_3'}
    }
}

print('Posting events...')
ok = ensure_price_rule()
if not ok:
    print('Warning: failed to ensure PRICE rule on deployed service')
for ev in (evt1, evt2, evt3, evt4):
    sign_and_post(ev)
    time.sleep(0.5)

print('\nWaiting 3s for worker to process...')
time.sleep(3)

print('\nGET /events')
try:
    r = requests.get(EVENTS_URL, timeout=30)
    print(r.status_code)
    print(r.text)
except Exception as e:
    print('events error', e)

print('\nGET /jobs')
try:
    r = requests.get(JOBS_URL, timeout=30)
    print(r.status_code)
    print(r.text)
except Exception as e:
    print('jobs error', e)

print('\nGET /stats')
try:
    r = requests.get(STATS_URL, timeout=30)
    print(r.status_code)
    print(r.text)
except Exception as e:
    print('stats error', e)

print('\nDone')
