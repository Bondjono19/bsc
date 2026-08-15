import redis
import csv 
import time
redis = redis.Redis(host="localhost",port="6379",password="password")
sub = redis.pubsub()
sub.subscribe('recognitionChannel')

with open("./data/received_events_offline_test.csv","w") as f:
    w = csv.writer(f)
    w.writerow(("timestamp","message","channel"))
    for message in sub.listen():
        if (message["type"] == "message"):
            content = message['data'].decode()
            w.writerow([time.time(),content])
            f.flush()
            print(f"Received: {content}")
