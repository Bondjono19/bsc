from datasets import load_dataset
import re
from collections import Counter

dataset = load_dataset("bitmind/lfw")
data = dataset["train"]

def get_name(filename):
    return re.sub(r'_\d+\.jpg$', '', filename)

names = [get_name(f) for f in data["filename"]]
count_names = Counter(names)
valid_names = {name for name, count in count_names.items() if count >=4}
invalid_names = {name for name, count in count_names.items() if count <=3}
plus_four_imgs = []
lt_four_imgs = []
for i in data:
    if(get_name(i["filename"]) in valid_names):
        plus_four_imgs.append(i)
    elif (get_name(i["filename"]) in invalid_names):
        lt_four_imgs.append(i)


print(f"4+ images: {len(valid_names)}")
print(f"total imgs: {len(plus_four_imgs)}")
print(f"3 or less images: {len(invalid_names)}")
print(f"total 3 or less imgs: {len(lt_four_imgs)}" )

with open("valid_names.txt","w") as f:
    for name in sorted(valid_names):
        f.write(name+"\n")


with open("probes.txt","w") as f:
    for name in sorted(valid_names):
        f.write(name+"_0001.jpg\n")
    count = 0
    for name in sorted(invalid_names):
        f.write(name+"_0001.jpg\n")
        count+=1
        if(count >= 1000):
            break

with open("gallery.txt","w") as f:
    for i in sorted(plus_four_imgs, key=lambda x: x["filename"]):
        num = re.search(r'_(\d+)\.jpg$', i["filename"]).group(1)
        n = int(num)
        if not(n > 5 or n == 1):
            f.write(i["filename"]+"\n")
