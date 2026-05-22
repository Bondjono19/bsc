import cv2
import time

cap = cv2.VideoCapture(0)

detector = cv2.FaceDetectorYN.create("face_detection_yunet_2023mar.onnx","",(800,448))

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
                        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
                
                        bounding_box = face[0:4]
                        landmarks = face[4:14]
                        transformation_matrix = cv2.estimateAffinePartial2D(landmarks)
        
        cv2.imshow("stream",frame)

        if(cv2.waitKey(1) & 0xFF == ord("q")):
                break

cap.release()
cv2.destroyAllWindows()