import cv2
import time
from imagedata import ImageData
from recognition.utils.get_points import get_reference_points
import time
import numpy as np
from recognition.recognitionService import recognitionService

cap = cv2.VideoCapture(0)
detector = cv2.FaceDetectorYN.create("models/face_detection_yunet_2023mar.onnx","",(800,448))
rp = np.asarray(get_reference_points(),dtype=np.float32).reshape(5,2)

while True:
        ret, frame = cap.read()
        if not ret:
                break

        _, faces = detector.detect(frame)
        if faces is not None:
                for face in faces:
                        x = int(face[0])
                        y = int(face[1])
                        w = int(face[2])
                        h = int(face[3])
                        #cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
                        bounding_box = face[0:4]
                        landmarks = face[4:14].reshape(5,2).astype(np.float32)
                        transformation_matrix = cv2.estimateAffinePartial2D(landmarks,rp)
                        aligned_img = cv2.warpAffine(frame,transformation_matrix[0],(112,122))
                        recognitionService.recognize(aligned_img)
        
        cv2.imshow("stream",frame)

cap.release()
cv2.destroyAllWindows()