from datasets import load_dataset
import re
from collections import Counter
import cv2
import numpy as np
import os
#utils
def get_name(filename):
    return re.sub(r'_\d+\.jpg$', '', filename)
detector = cv2.FaceDetectorYN.create("./../models/face_detection_yunet_2023mar.onnx","",(250,250))


#data preprocess
dataset = load_dataset("bitmind/lfw")
data = dataset["train"]

images = {x["filename"]: x["image"] for x in data}


names = [get_name(f) for f in data["filename"]]
count_names = Counter(names)
valid_names = {name for name, count in count_names.items() if count >=3}
invalid_names = {name for name, count in count_names.items() if count <=2}
plus_three_imgs = []
lt_three_imgs = []
for i in data:
    if(get_name(i["filename"]) in valid_names):
        plus_three_imgs.append(i)
    elif (get_name(i["filename"]) in invalid_names):
        lt_three_imgs.append(i)


print(f"3+ image names: {len(valid_names)}")
print(f"total imgs 3+: {len(plus_three_imgs)}")
print(f"2 or less image names: {len(invalid_names)}")
print(f"total 3 or less imgs: {len(lt_three_imgs)}" )


with open("data/mt_three_cleaned.txt","w") as f:
    for item in sorted(plus_three_imgs, key=lambda x: x["filename"]):
        image = images[item["filename"]]
        cv_img = np.array(image)
        cv_img = cv2.cvtColor(cv_img,cv2.COLOR_RGB2BGR)
        h,w,_ = cv_img.shape
        detector.setInputSize((w,h))
        _, faces = detector.detect(cv_img)
        if faces is None:
            continue
        if not len(faces)==1:
            continue
        f.write(item["filename"]+"\n")

with open("data/lt_three_cleaned.txt","w") as f:
    for item in sorted(lt_three_imgs, key=lambda x: x["filename"]):
        image = images[item["filename"]]
        cv_img = np.array(image)
        cv_img = cv2.cvtColor(cv_img,cv2.COLOR_RGB2BGR)
        h,w,_ = cv_img.shape
        detector.setInputSize((w,h))
        _, faces = detector.detect(cv_img)
        if faces is None:
            continue
        if not len(faces)==1:
            continue
        f.write(item["filename"]+"\n")

with open("data/mt_three_cleaned.txt","r") as f:
    lines_mt_three_cleaned = f.readlines()

with open("data/lt_three_cleaned.txt","r") as f:
    lines_lt_three_cleaned = f.readlines()

counts = Counter(get_name(line.strip()) for line in lines_mt_three_cleaned)

with open("data/gallery.txt","w") as f:
    ctr = 0
    prev_name = ""
    for line in lines_mt_three_cleaned:
        name = get_name(line.strip())
        if name == prev_name:
            ctr+=1
        else:
            ctr=1
        if counts[name] >= 3 and ctr < 6:
            f.write(line)
        prev_name = name

withheld_probe_imgs = []
with open("data/gallery.txt","r") as f:
    gallery_lines = f.readlines()

prev_name = ""
new_gallery = []
for line in gallery_lines:
    name = get_name(line.strip())
    if(name!=prev_name):
        withheld_probe_imgs.append(line.strip())
    else:
        new_gallery.append(line)
    prev_name = name

with open("data/probes.txt","w") as f:
    ctr = 0
    for line in lines_lt_three_cleaned:
        num = re.search(r'_(\d+)\.jpg$', line).group(1)
        if num=="0001":
            f.write(line)
            ctr+=1
            if ctr >= 1000:
                break

with open("data/probes.txt", "a") as f:
    for filename in withheld_probe_imgs:
        f.write(filename+"\n")

with open("data/gallery.txt", "w") as f:
    for filename in new_gallery:
        f.write(filename)


#get list of unique gallery names:
with open("data/gallery.txt","r") as f:
    gallery_names = set(get_name(line.strip()) for line in f)

with open("data/unique_gallery_names.txt","w") as f:
    for name in gallery_names:
        f.write(name+"\n")