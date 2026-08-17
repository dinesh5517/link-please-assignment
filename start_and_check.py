import os, requests, json
base='https://pseudogram-api.onrender.com'
# load key from .env next to script
PSEUDO_KEY=None
try:
    with open(os.path.join(os.path.dirname(__file__) or '.', '.env'),'r',encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith('#'): continue
            if '=' in line:
                k,v=line.split('=',1)
                if k.strip()=='PSEUDOGRAM_API_KEY': PSEUDO_KEY=v.strip(); break
except Exception as e:
    pass
if not PSEUDO_KEY:
    print('no key')
    raise SystemExit(1)
headers={'X-API-Key':PSEUDO_KEY}
start = requests.post(base+'/v1/simulate/start', headers=headers, json={'webhook_url':'https://link-please-assignment.onrender.com/webhook','count':5,'duration_seconds':2}, timeout=15)
print('start status', start.status_code, start.text)
run_id = None
try:
    run_id=start.json().get('run_id')
except Exception:
    pass
if not run_id:
    print('no run id')
    raise SystemExit(1)
print('run_id', run_id)
truth_url=f"{base}/v1/simulate/{run_id}/truth"
print('GET', truth_url)
resp = requests.get(truth_url, headers=headers, timeout=15)
print('truth status', resp.status_code)
print(resp.text)
