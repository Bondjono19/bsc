import cv2
import numpy as np
from cv2.typing import MatLike
from imagedata import ImageData
import onnxruntime as oxrt
import asyncio
from recognition.utils.get_points import get_reference_points
from shared.database.databaseManager import databaseManager
from shared.database.models import Identity

class InsertionService:
    def __init__(self):
        self.camera_dimensions = (800,448)
        self.model_path = "models/edgeface_xs_gamme_06.onnx"
        self.detector = None
        self.recognizer = None
        self.reference_points = None
        self.thread = None
        self.thread_running = None
        self.cap = cv2.VideoCapture(0)
        self.all_identities = None
        self.threshold = 0.5
        self.detector = cv2.FaceDetectorYN.create("models/face_detection_yunet_2023mar.onnx","",self.camera_dimensions)
        self.recognizer = oxrt.InferenceSession("models/edgeface_xs_gamme_06.onnx",providers=["CPUExecutionProvider"])
        self.reference_points = np.asarray(get_reference_points(),dtype=np.float32).reshape(5,2)
        self.identities = []
    
    
    def compare(self,v1,v2):
        return (np.dot(v1,v2)) / (np.linalg.norm(v1)*np.linalg.norm(v2))

    def compare_faces(self, embedding: np.ndarray):
        best_similarity = (0,None)
        for identity in self.identities:
            sim = self.compare(embedding,identity[2])
            if (sim > best_similarity):
                best_similarity[0] = sim
                best_similarity[1] = identity

        return best_similarity
        #DB face iterations
        

    def preprocess_tensor(self,frame):
        tensor = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        #Convnert datatype
        tensor = tensor.astype(np.float32) / 255.0
        #normalize -1 to 1
        tensor = (tensor - 0.5) / 0.5
        #Convert datatype
        tensor = tensor.astype(np.float32)
        #change and add dimension
        tensor = np.transpose(tensor,(2,0,1))
        tensor = np.expand_dims(tensor,axis=0)
        return np.ascontiguousarray(tensor)

    def recognize_face(self,frame: MatLike):
        tensor = self.preprocess_tensor(frame)
        embedding = self.recognizer.run(None, {"input.1": tensor})
        return embedding

    def detect_face(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            _, faces = self.detector.detect(frame)
            if faces is not None:
                for face in faces:
                    landmarks = face[4:14].reshape(5,2).astype(np.float32)
                    transformation_matrix = cv2.estimateAffinePartial2D(landmarks,self.reference_points)
                    aligned_image = cv2.warpAffine(frame,transformation_matrix[0],(112,112))
                    embedding = self.recognize_face(aligned_image)
                    name = input()
                    databaseManager.add(Identity(name,embedding))


    def watch_detect():
        pass


