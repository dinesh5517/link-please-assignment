import os
import hmac
import hashlib
import json
import time
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app

KEY = os.getenv('PSEUDOGRAM_API_KEY')
if not KEY:
    # attempt to load from .env in repo root
    from dotenv import load_dotenv
    load_dotenv()
    KEY = os.getenv('PSEUDOGRAM_API_KEY')

if not KEY:
    print('PSEUDOGRAM_API_KEY not found in env or .env')
    raise SystemExit(2)

client = TestClient(app)

headers_base = {'Content-Type':'application/json'}

def sign_headers(body_bytes):
    sig = hmac.new(KEY.encode(), body_bytes, hashlib.sha256).hexdigest()
    return {**headers_base, 'X-PseudoGram-Signature': 'sha256=' + sig}


def create_price_rule():
    payload = {'keyword': 'PRICE', 'dm_message': 'Local PRICE DM'}
    r = client.post('/rules', json=payload)
    print('create rule ->', r.status_code, r.json())


def post_event(ev):
    body = json.dumps(ev, separators=(',',':')).encode()
    headers = sign_headers(body)
    r = client.post('/webhook', data=body, headers=headers)
    print('POST', ev['event_type'], '->', r.status_code, r.json())
    return r


def show_state():
    print('\n/events ->', client.get('/events').status_code, client.get('/events').json())
    print('/jobs ->', client.get('/jobs').status_code, client.get('/jobs').json())
    print('/stats ->', client.get('/stats').status_code, client.get('/stats').json())


def run_local_check():
    create_price_rule()

    user = 'local_user_1'
    c = 'local_c_1'

    ev_created = {
        'event_id': f'levt_{uuid4().hex[:8]}',
        'event_type': 'comment.created',
        'data': {
            'comment_id': c,
            'post_id': 'p1',
            'text': 'Please show PRICE list',
            'from': {'user_id': user}
        }
    }

    ev_accepted = {
        'event_id': f'levt_{uuid4().hex[:8]}',
        'event_type': 'comment.accepted',
        'data': {
            'comment_id': 'local_c_2',
            'post_id': 'p1',
            'text': 'Can I see the PRICE please',
            'from': {'user_id': 'local_user_2'}
        }
    }

    ev_deleted = {
        'event_id': f'levt_{uuid4().hex[:8]}',
        'event_type': 'comment.deleted',
        'data': {
            'comment_id': c
        }
    }

    # Post created -> should create job
    post_event(ev_created)
    time.sleep(0.2)
    # Post accepted -> should create job
    post_event(ev_accepted)
    time.sleep(0.2)
    # Post deleted -> should cancel queued job for comment c
    post_event(ev_deleted)

    # Allow worker to run a short time
    time.sleep(2)

    show_state()

if __name__ == '__main__':
    run_local_check()
