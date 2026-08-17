import time
import concurrent.futures
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def setup_rules():
    res = client.post("/rules", json={"keyword": "PRICE", "dm_message": "Price list: $99"})
    print("Created rule:", res.json())

def send_comment_event(idx):
    user_id = f"usr_{idx % 50}"  # 50 unique users among 500 comments
    event_id = f"evt_{idx}"
    comment_id = f"cmt_{idx}"
    
    payload = {
        "event_id": event_id,
        "event_type": "comment.created",
        "sent_at": "2026-08-10T09:14:22.481Z",
        "data": {
            "comment_id": comment_id,
            "post_id": "post_1",
            "text": f"PRICE query {idx}",
            "created_at": "2026-08-10T09:14:21.900Z",
            "from": {
                "user_id": user_id,
                "username": f"user_{user_id}"
            }
        }
    }
    
    start_time = time.time()
    res = client.post("/webhook", json=payload)
    duration = time.time() - start_time
    return res.status_code, duration

def run_simulation():
    setup_rules()
    
    print("Starting 500 events load test...")
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(send_comment_event, i) for i in range(500)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    total_time = time.time() - start_time
    
    status_codes = [r[0] for r in results]
    durations = [r[1] for r in results]
    
    print(f"Completed 500 events in {total_time:.2f} seconds.")
    print(f"Status codes: 200 count = {status_codes.count(200)}, total = {len(status_codes)}")
    print(f"Max response time: {max(durations):.4f}s, Avg response time: {sum(durations)/len(durations):.4f}s")
    
    res_stats = client.get("/stats")
    print("Stats after simulation:", res_stats.json())

if __name__ == "__main__":
    run_simulation()
