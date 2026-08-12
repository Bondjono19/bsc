import csv

with open("data/t2_results.csv") as f:
    r = csv.DictReader(f)
    totals = [float(row["total_in_ms"]) for row in r]

totals.sort()
percentile95th = totals[int(len(totals)*0.95)]
print(f"Total Runs: {len(totals)}")
print(f"95th percentile is: {percentile95th:.2f} ms")
print(f"Minimum: {min(totals):.2f} ms")
print(f"Maximum: {max(totals):.2f} ms")
