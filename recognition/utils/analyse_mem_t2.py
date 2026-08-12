import csv

with open("data/sysmon.csv") as f:
    r = csv.DictReader(f)
    rows_in_file = list(r)

memory = [int(r["memory_available_in_mb"]) for r in rows_in_file]
swapping = [int(r["swap_used_in_mb"]) for r in rows_in_file]
timestamps = [int(r["timestamp"]) for r in rows_in_file]
duration = (timestamps[-1] - timestamps[0]) / 60
throttled = [r["throttled_status"] for r in rows_in_file]
all_clean_or_not = all(t == "0x0" for t in throttled)
temps = [float(r["temperature_in_c"]) for r in rows_in_file]

print(f"Minimum available memory: {min(memory)} MB")
print(f"Max swap used: {max(swapping)} MB")
print(f"Total time duration: {duration:.1f} minutes")
print(f"Any throttle occurances not 0x0: {not all_clean_or_not}")
print(f"Min temp: {min(temps)} C")
print(f"Max temp: {max(temps)} C")
print(f"Avg temp: {sum(temps)/len(temps):.1f} C")