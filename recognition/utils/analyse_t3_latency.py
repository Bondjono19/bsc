import csv
import numpy as np
import re

# Parse ID from content string
def extract_id(text):
    match = re.search(r"ID: (\d+)", text)
    return int(match.group(1)) if match else None

# Load sent events
with open("data/sent_events_broker_test.csv") as f:
    reader = csv.DictReader(f)
    sent = {extract_id(row["content"]): float(row["timestamp"]) for row in reader}

# Load received events
with open("data/received_events_broker_test.csv") as f:
    reader = csv.DictReader(f)
    received = {extract_id(row["message"]): float(row["timestamp"]) for row in reader}

# Match by ID up to 3233
latencies = []
for id in range(3234):
    if id in sent and id in received:
        latencies.append((received[id] - sent[id]) * 1000)
    else:
        print(f"Missing ID {id}")

latencies = np.array(latencies)

print(f"Matched: {len(latencies)}")
print(f"Min:  {np.min(latencies):.2f} ms")
print(f"Max:  {np.max(latencies):.2f} ms")
print(f"Avg:  {np.mean(latencies):.2f} ms")
print(f"Std:  {np.std(latencies):.2f} ms")