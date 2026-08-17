import csv
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde


with open("data/t_8_results.csv") as f:
    r = csv.DictReader(f)
    rows = list(r)

timestamps = [float(r["timestamp"]) for r in rows]
ite_ms = [float(r["iteration_ms"]) for r in rows]

print(f"Total frames: {len(rows)}")
print(f"Min iteration: {np.min(ite_ms):.2f} ms")
print(f"Max iteration: {np.max(ite_ms):.2f} ms")
print(f"avg ite: {np.mean(ite_ms):.2f} ms")
print(f"Std dev: {np.std(ite_ms):.2f} ms")

t_start = timestamps[0]
buckets = [int(t-t_start) for t in timestamps]
max_bucket = max(buckets)
fps1 = []
for i in range(max_bucket + 1):
    c = buckets.count(i)
    fps1.append(c)

fps = np.array(fps1)

print(f"total 1 second intervals: {len(fps)}")
print(f"min fps: {np.min(fps)}")
print(f"max fps: {np.max(fps)}")
print(f"min fps: {np.mean(fps)}")
print(f"5th percentile: {np.percentile(fps,5):.2f}")

import csv
import matplotlib.pyplot as plt
import numpy as np

with open("data/t_8_results.csv") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

totals = [float(r["iteration_ms"]) for r in rows]

plt.figure(figsize=(8, 5))
plt.hist(fps, bins=50, density=True, alpha=0.7, label="Distribution")
plt.axvline(x=10, color="r", linestyle="--", label="limit")
plt.axvline(x=np.percentile(fps, 5), color="orange", linestyle="--", label=f"5th percentile ({np.percentile(fps, 5):.0f} ms)")
plt.xlabel("1 Second Intervals")
plt.ylabel("Frequency")
plt.title("Distribution of FPS during T8")
plt.legend()
plt.savefig("FPS_distribution.png", dpi=150, bbox_inches="tight")
plt.show()