import requests, time, json, sys, os

# Allow overriding count/duration via CLI: run_simulation.py [count] [duration_seconds]
args = sys.argv[1:]
COUNT = int(args[0]) if len(args) > 0 else 500
DURATION = int(args[1]) if len(args) > 1 else 10

WEBHOOK_URL='https://link-please-assignment.onrender.com/webhook'
STATS_URL='https://link-please-assignment.onrender.com/stats'

# Output files saved next to this script
SCRIPT_DIR = os.path.dirname(__file__) or '.'
OUT_TRUTH = os.path.join(SCRIPT_DIR, 'truth.json')
OUT_DEPLOYED = os.path.join(SCRIPT_DIR, 'deployed_stats.json')

# read API key from environment or .env file (local)
# (os already imported)
PSEUDO_KEY = os.getenv('PSEUDOGRAM_API_KEY')
if not PSEUDO_KEY:
    # try local .env file located next to this script
    try:
        base = os.path.dirname(__file__) or '.'
        env_path = os.path.join(base, '.env')
        with open(env_path,'r', encoding='utf-8') as f:
            for line in f:
                line=line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    k,v=line.split('=',1)
                    if k.strip()=='PSEUDOGRAM_API_KEY':
                        PSEUDO_KEY=v.strip()
                        break
    except Exception:
        PSEUDO_KEY=None
if not PSEUDO_KEY:
    print('Missing PSEUDOGRAM_API_KEY in env or .env; aborting')
    sys.exit(1)
HEADERS={'X-API-Key': PSEUDO_KEY}
print('Checking /stats...')
try:
    r=requests.get(STATS_URL, timeout=10)
    print('stats', r.status_code, r.text)
except Exception as e:
    print('stats check failed', e)

print('\nStarting 500-event simulation...')
start = requests.post('https://pseudogram-api.onrender.com/v1/simulate/start', headers=HEADERS, json={'webhook_url':WEBHOOK_URL,'count':COUNT,'duration_seconds':DURATION}, timeout=10)
print('start', start.status_code, start.text)
try:
    run_id = start.json().get('run_id')
except Exception:
    run_id = None
if not run_id:
    print('No run_id returned; aborting')
    sys.exit(1)
print('run_id=', run_id)

# Poll for truth
truth_url=f'https://pseudogram-api.onrender.com/v1/simulate/{run_id}/truth'
print('Polling truth at', truth_url)
for i in range(120):
    try:
        rt = requests.get(truth_url, headers=HEADERS, timeout=10)
    except Exception as e:
        print('poll error', e)
        rt = None
    if rt is not None and rt.status_code==200:
        try:
            data = rt.json()
        except Exception as e:
            print('invalid json', e)
            data = rt.text
        # If grader reports status and it's not complete yet, continue polling
        if isinstance(data, dict) and data.get('status') and data.get('status') != 'complete':
            print(f"Grader status: {data.get('status')}, waiting")
        else:
            print('TRUTH fetched: events=', len(data.get('events', [])) if isinstance(data, dict) else 'unknown')
            with open(OUT_TRUTH,'w', encoding='utf-8') as f:
                json.dump(data, f)
            break
    else:
        status = rt.status_code if rt is not None else 'noresponse'
        print(f'Attempt {i+1}: truth not ready ({status}), waiting 2s...')
        time.sleep(2)
else:
    print('Truth not available after polling; exiting')

# Fetch deployed stats after simulation
try:
    s = requests.get(STATS_URL, timeout=10)
    print('Deployed /stats after run:', s.status_code, s.text)
    with open(OUT_DEPLOYED,'w', encoding='utf-8') as f:
        json.dump(s.json(), f)
except Exception as e:
    print('Failed to fetch deployed stats', e)
