import csv
import matplotlib.pyplot as plt
import numpy as np

with open("data/t2_results.csv") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

detection = np.mean([float(r["detection_in_ms"]) for r in rows])
alignment = np.mean([float(r["alignment_in_ms"]) for r in rows])
embedding = np.mean([float(r["embedding_in_ms"]) for r in rows])
comparison = np.mean([float(r["comparison_in_ms"]) for r in rows])

std_dev_detection = np.std([float(r["detection_in_ms"]) for r in rows])
std_dev_alignment = np.std([float(r["alignment_in_ms"]) for r in rows])
std_dev_embedding= np.std([float(r["embedding_in_ms"]) for r in rows])
std_dev_comparison = np.std([float(r["comparison_in_ms"]) for r in rows])

print(f"std_dev_detection: {std_dev_detection:.2f}")
print(f"std_dev_alignment: {std_dev_alignment:.2f}")
print(f"std_dev_embedding: {std_dev_embedding:.2f}")
print(f"std_dev_comparison: {std_dev_comparison:.2f}")

print(f"detection mean: {detection:.2f}")
print(f"alignment mean: {alignment:.2f}")
print(f"Embedding mean: {embedding:.2f}")
print(f"Comparison mean:{comparison:.2f}")

labels = ["Detection", "Alignment", "Embedding", "Comparison"]
values = [detection, alignment, embedding, comparison]

plt.figure(figsize=(7, 5))
plt.bar(labels, values)
plt.ylabel("Time in ms")
plt.title("Average Duration of each Pipeline Stage during T2")
plt.savefig("stage_breakdown.png", dpi=200, bbox_inches="tight")
plt.show()