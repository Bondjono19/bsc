import csv
import numpy as np

with open("data/api_calls_latency.csv") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

post = [float(r["time_ms_post"]) for r in rows]
delete = [float(r["time_ms_del"]) for r in rows]

for name, vals in [("POST", post), ("DELETE", delete)]:
    print(f"--- {name} ---")
    print(f"Min:    {np.min(vals):.2f} ms")
    print(f"Max:    {np.max(vals):.2f} ms")
    print(f"Avg:    {np.mean(vals):.2f} ms")
    print(f"Std:    {np.std(vals):.2f} ms")
    print()