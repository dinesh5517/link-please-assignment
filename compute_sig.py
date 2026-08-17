import os, hmac, hashlib, json, argparse

# Load key from env or .env
def load_key():
    key = os.getenv('PSEUDOGRAM_API_KEY')
    if key:
        return key
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith('PSEUDOGRAM_API_KEY='):
                    return line.split('=',1)[1].strip()
    return None


def compute_signature(key: str, body_bytes: bytes) -> str:
    return hmac.new(key.encode(), body_bytes, hashlib.sha256).hexdigest()


def main():
    p = argparse.ArgumentParser(description='Compute HMAC-SHA256 signature for webhook body')
    p.add_argument('--body', help='Body JSON string to sign. If omitted, a default test body is used.')
    args = p.parse_args()

    key = load_key()
    if not key:
        raise SystemExit('PSEUDOGRAM_API_KEY not found in env or .env')

    if args.body:
        # Ensure we sign the exact bytes provided
        body_bytes = args.body.encode('utf-8')
    else:
        payload = {"event_id":"1","event_type":"comment.created","data":{"comment_id":"c1","text":"PRICE","from":{"user_id":"u1"}}}
        body_bytes = json.dumps(payload, separators=(",",":" )).encode()

    sig = compute_signature(key, body_bytes)
    print('sha256=' + sig)


if __name__ == '__main__':
    main()
