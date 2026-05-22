import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import time
from imagedata import ImageData
from recognition.utils.get_points import get_reference_points
import time
import numpy as np
from recognition.recognitionService import recognitionService

detector = cv2.FaceDetectorYN.create("models/face_detection_yunet_2023mar.onnx","",(175,289))
rp = np.asarray(get_reference_points(),dtype=np.float32).reshape(5,2)

img = cv2.imread("imgs/messi1.jpg")

if img is None:
    raise FileNotFoundError()

_, faces = detector.detect(img)

if faces is not None:
                for face in faces:
                        print("face detected")
                        x = int(face[0])
                        y = int(face[1])
                        w = int(face[2])
                        h = int(face[3])
                        #cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
                        bounding_box = face[0:4]
                        landmarks = face[4:14].reshape(5,2).astype(np.float32)
                        transformation_matrix = cv2.estimateAffinePartial2D(landmarks,rp)
                        aligned_img = cv2.warpAffine(img,transformation_matrix[0],(112,112))
                        print(aligned_img)
                        cv2.imwrite("aligned_imgmessi1.png",aligned_img)
                        recognitionService.recognize(aligned_img)