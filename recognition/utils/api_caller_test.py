import time
import requests
import random
import string
import csv
f = open("data/api_calls_latency_t7.csv", "w", newline="")
w = csv.writer(f)
w.writerow(["timestamp","time_ms_post","time_ms_del","response_code_post","response_code_del","id"])
uname = "efghi"
globalid = 2000
embedding1 = [random.uniform(-1,1) for i in range(512)]
embedding2 = [random.uniform(-1,1) for i in range(512)]
URL = "http://192.168.68.58:8000/identities/"
t_start = time.time()
t_end = t_start + 600

while time.time() < t_end:
    t_post_start = time.perf_counter()

    res_post = requests.post(
        URL+"create",
        json = {
            "name" : uname,
            "globalid" : globalid,
            "embeddings" : [
                embedding1,
                embedding2
            ]
        },
        headers= {"Authorization": "Bearer test"}
    )

    t_post_end = time.perf_counter()

    post_status_code = res_post.status_code
    data = res_post.json()
    id = data["id"]

    t_del_start = time.perf_counter()

    res_del = requests.delete(
        URL+"remove",
        json = {
            "id" : id
        },
        headers= {"Authorization": "Bearer test"}
    )

    del_status_code = res_del.status_code

    t_del_end = time.perf_counter()

    w.writerow([
        time.time(),
        (t_post_end - t_post_start)*1000,
        (t_del_end - t_del_start) * 1000,
        post_status_code,
        del_status_code,
        id
    ])

    time.sleep(55)
    globalid+=1
    uname = "".join(random.choices(string.ascii_letters,k=4))

f.close()