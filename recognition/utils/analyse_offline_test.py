import csv
import re
import sys
import statistics

SENT_PATH = sys.argv[1] if len(sys.argv) > 1 else "data/sent_events_offline_test.csv"
RECV_PATH = sys.argv[2] if len(sys.argv) > 2 else "data/received_events_offline_test.csv"
THRESHOLD = 0.52
MAX_LATENCY = 60.0


def load(path, content_col):
    rows = {}
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            content = row[content_col]
            m = re.search(r"LOG_ID:\s*(\d+)", content)
            if not m:
                continue
            log_id = int(m.group(1))
            s = re.search(r"(\d+\.\d+)\s+similarity score|max sim score:\s*(\d+\.\d+)", content)
            score = None
            if s:
                score = float(s.group(1) or s.group(2))
            rows[log_id] = {"timestamp": float(row["timestamp"]), "content": content, "score": score}
    return rows


sent = load(SENT_PATH, "content")
recv = load(RECV_PATH, "message")

print(f"Sent events:     {len(sent)}")
print(f"Received events: {len(recv)}")
print("PASS: counts equal" if len(sent) == len(recv) else "FAIL: counts differ")

missing = set(sent) - set(recv)
extra = set(recv) - set(sent)
print("PASS: every sent event received" if not missing else f"FAIL: missing {sorted(missing)}")
if extra:
    print(f"Warning: extra received {sorted(extra)}")

above = [lid for lid, r in sent.items() if r["score"] is not None and r["score"] > THRESHOLD]
below = [lid for lid, r in sent.items() if r["score"] is not None and r["score"] <= THRESHOLD]
print(f"\nEvents above {THRESHOLD}: {len(above)}")
print(f"Events at or below {THRESHOLD}: {len(below)}")

latest_sent = max(r["timestamp"] for r in sent.values())
late = [lid for lid, r in recv.items() if r["timestamp"] - latest_sent > MAX_LATENCY]
print(f"\nLatest sent timestamp: {latest_sent:.3f}")
print(f"Events received more than {MAX_LATENCY}s after latest sent: {len(late)}")
if late:
    print(f"  {sorted(late)}")

latest_recv = max(r["timestamp"] for r in recv.values())
print(f"Latest received timestamp: {latest_recv:.3f}")
print(f"Latest received minus latest sent: {latest_recv - latest_sent:.3f} s")