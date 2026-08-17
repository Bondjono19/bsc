import csv
import matplotlib.pyplot as plt
import numpy as np

with open("data/t2_results.csv") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

totals = [float(r["total_in_ms"]) for r in rows]

plt.figure(figsize=(8, 5))
plt.hist(totals, bins=50, density=True, alpha=0.7, label="Distribution")
plt.axvline(x=500, color="r", linestyle="--", label="500 ms limit")
plt.axvline(x=np.percentile(totals, 95), color="orange", linestyle="--", label=f"95th percentile ({np.percentile(totals, 95):.0f} ms)")
plt.xlabel("Total Pipeline Time (ms)")
plt.ylabel("Frequency")
plt.title("Distribution of Processing Performance during T2")
plt.legend()
plt.savefig("performance_distribution.png", dpi=150, bbox_inches="tight")
plt.show()