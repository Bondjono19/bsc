import cv2
import numpy as np
import time
import os
from cv2.typing import MatLike
import onnxruntime as oxrt
import asyncio

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
from recognition.utils.get_points import get_reference_points
from shared.database.databaseManager import databaseManager
from shared.database.models import Identity,Embedding

class RecognitionService:
    def __init__(self):
        self.camera_dimensions = (800,448)
        self.model_path = os.path.join(MODELS_DIR, "edgeface_xs_gamme_06.onnx")
        self.detector = None
        self.recognizer = None
        self.reference_points = None
        self.thread = None
        self.thread_running = None
        self.cap = None
        self.all_identities = None
        self.threshold = 0.5

    async def __aenter__(self):
        self.detector = cv2.FaceDetectorYN.create(os.path.join(MODELS_DIR, "face_detection_yunet_2023mar.onnx"),"",self.camera_dimensions)
        self.recognizer = oxrt.InferenceSession(os.path.join(MODELS_DIR, "edgeface_xs_gamme_06.onnx"),providers=["CPUExecutionProvider"])
        self.reference_points = np.asarray(get_reference_points(),dtype=np.float32).reshape(5,2)
        self.identities = []
        await self.load_identites()
        self.thread = asyncio.create_task(asyncio.to_thread(self.detect_face))
        self.thread_running = True
        return self
    
    async def load_identites(self):
        identities = await databaseManager.fetchAll(Identity)
        for identity in identities:
            embeddings = identity.embeddings
            for embedding in embeddings:
                vector = np.asarray(embedding.vector,dtype=np.float32)
                self.identities.append((identity.id,identity.global_id,identity.name,vector))

    async def __aexit__(self, exc_type, exc, tb):
        self.thread_running = False
        await self.thread
        self.cap.release()
    
    def compare(self,v1,v2):
        return (np.dot(v1,v2)) / (np.linalg.norm(v1)*np.linalg.norm(v2))

    def compare_faces(self, embedding: np.ndarray):
        best_similarity = (0,None)
        for identity in self.identities:
            sim = self.compare(embedding,identity[3])
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
            self.cap = cv2.VideoCapture(0)
            ret, frame = self.cap.read()
            if not (self.cap.isOpened()):
                break
            if not ret:
                break
            _, faces = self.detector.detect(frame)
            if faces is not None:
                for face in faces:
                    landmarks = face[4:14].reshape(5,2).astype(np.float32)
                    transformation_matrix = cv2.estimateAffinePartial2D(landmarks,self.reference_points)
                    aligned_image = cv2.warpAffine(frame,transformation_matrix[0],(112,112))
                    embedding = self.recognize_face(aligned_image)
                    result = self.compare_faces(np.asarray(embedding,dtype=np.float32).flatten())
                    if(result>self.threshold):
                        print(f"Detected: {result[1][2]} with local id {result[1][0]} at {result[0]} similarity score")


    def watch_detect():
        pass

recognitionService = RecognitionService()

#--- INSERT NEW IDENTITES
def insert_face(recognitionService: RecognitionService):
    while True:
        recognitionService.cap = cv2.VideoCapture(0)
        input("Type anything to capture")
        ret, frame = recognitionService.cap.read()
        if not (recognitionService.cap.isOpened()): 
            break
        if not ret:
            break
        _, faces = recognitionService.detector.detect(frame)
        if faces is not None:
            for face in faces:
                landmarks = face[4:14].reshape(5,2).astype(np.float32)
                transformation_matrix = cv2.estimateAffinePartial2D(landmarks,recognitionService.reference_points)
                aligned_image = cv2.warpAffine(frame,transformation_matrix[0],(112,112))
                embedding = recognitionService.recognize_face(aligned_image)
                p_list = embedding.tolist()
                identity_id = input("identity_id: ")
                embedding_obj = databaseManager.add(Embedding(identity_id=identity_id,vector=p_list))
                print(f"added: {embedding_obj}")
                input("type to continue")



if __name__ == "__main__":
    recognitionService.detect_face()