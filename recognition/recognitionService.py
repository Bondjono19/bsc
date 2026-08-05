import cv2
import numpy as np
import time
import os
import json
from cv2.typing import MatLike
import onnxruntime as oxrt
import asyncio
import traceback
from recognition.utils.get_points import get_reference_points
from shared.database.databaseManager import databaseManager
from shared.database.models import Identity,Embedding, Event
from recognition.eventConnectionService import eventConnectionService
from recognition.accessGrantor import accessGrantorExample
from skimage.transform import SimilarityTransform
MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")


class RecognitionService:
    def __init__(self, detection_mode: bool):
        self.detection_mode = detection_mode
        self.camera_dimensions = (640,480)
        self.model_path = os.path.join(MODELS_DIR, "edgeface_xs_gamme_06.onnx")
        self.detector = None
        self.recognizer = None
        self.reference_points = None
        self.thread = None
        self.thread_running = None
        self.cap = None
        self.all_identities = None
        self.threshold = 0.5
        self.loop = None

    async def __aenter__(self):
        self.detector = cv2.FaceDetectorYN.create(os.path.join(MODELS_DIR, "face_detection_yunet_2023mar.onnx"),"",self.camera_dimensions)
        self.recognizer = oxrt.InferenceSession(os.path.join(MODELS_DIR, "edgeface_xs_gamme_06.onnx"),providers=["CPUExecutionProvider"])
        self.reference_points = np.asarray(get_reference_points(),dtype=np.float32).reshape(5,2)
        self.identities = []
        self.loop = asyncio.get_running_loop()
        await self.load_identites()
        if(self.detection_mode):
            self.thread = asyncio.create_task(asyncio.to_thread(self.detect_face))
            self.thread_running = True
        else:
            self.thread = asyncio.create_task(asyncio.to_thread(self.insert_face))
            self.thread_running = True
        return self
    
    async def load_identites(self):
        identities = await databaseManager.fetchAll(Identity, Identity.embeddings)
        if identities is not None:
            for identity in identities:
                embeddings = identity.embeddings
                for embedding in embeddings:
                    vector = np.asarray(embedding.vector,dtype=np.float32)
                    self.identities.append((identity.id,identity.global_id,identity.name,vector))

    async def __aexit__(self, exc_type, exc, tb):
        self.thread_running = False
    
    def compare(self,v1,v2):
        return (np.dot(v1,v2)) / (np.linalg.norm(v1)*np.linalg.norm(v2))

    def compare_faces(self, embedding: np.ndarray):
        best_similarity = [0,None]
        for identity in self.identities:
            sim = self.compare(embedding,identity[3])
            if (sim > best_similarity[0]):
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
        return np.asarray(embedding[0],dtype=np.float32).flatten()

    def detect_face(self):
        try:
            self.cap = cv2.VideoCapture(0,cv2.CAP_V4L2)
            while self.thread_running:
                try:
                    if not self.cap.isOpened():
                        print("No cam found")
                        break
                    print("watching")
                    ret, frame = self.cap.read()
                    h,w, _ = frame.shape
                    if not (self.cap.isOpened()):
                        print("broke loop, cap not open")
                        break
                    if not ret:
                        print("no ret")
                        break
                    self.detector.setInputSize((w,h))
                    _, faces = self.detector.detect(frame)
                    print(faces)
                    if faces is not None:
                        for face in faces:
                            landmarks = face[4:14].reshape(5,2).astype(np.float32)
                            transformation_matrix = SimilarityTransform.from_estimate(landmarks,self.reference_points)#cv2.estimateAffinePartial2D(landmarks,self.reference_points)
                            aligned_image = cv2.warpAffine(frame,transformation_matrix.params[0:2, :],(112,112))
                            embedding = self.recognize_face(aligned_image)
                            result = self.compare_faces(np.asarray(embedding,dtype=np.float32).flatten())
                            response: str
                            access = result[0]>self.threshold
                            if(access):
                                response = f"Detected: {result[1][2]} with local id {result[1][0]} at {result[0]} similarity score"
                                print(response)
                            else:
                                response = f"Face detected, no match in DB, max sim score: {result[0]}"
                                print(response)
                            #fire and forget event
                            asyncio.run_coroutine_threadsafe(eventConnectionService.publish(Event(direction="outbound",content=response, channel=eventConnectionService.channel,status="pending")),self.loop)
            
                            if(access):
                                #call child class that implements grantAccess interface and pass optional data. Here name for instance.
                                accessGrantorExample.grantAccess(result[1][2])
                except Exception as e:
                    print(e)
                    raise
        except Exception as e:
            print(e)
            self.thread_running = False
        finally:
            if(self.cap.isOpened()):
                self.cap.release()
    '''
        Comments on insert_face()
        Used during dev to insert faces into the system, not part of original architecture
    '''
    def insert_face(self):
        while self.thread_running:
            try:
                self.cap = cv2.VideoCapture(0,cv2.CAP_V4L2)
                if not self.cap.isOpened():
                    print("No cam found!")
                    return
                print("watching")
                input("Type anything to capture")
                if not (self.cap.isOpened()): 
                    break
                ret, frame = recognitionService.cap.read()
                h,w, _ = frame.shape
                if not ret:
                    break
                self.detector.setInputSize((w,h))
                _, faces = recognitionService.detector.detect(frame)
                print(faces)
                if faces is not None:
                    for face in faces:
                        landmarks = face[4:14].reshape(5,2).astype(np.float32)
                        transformation_matrix = cv2.estimateAffinePartial2D(landmarks,recognitionService.reference_points)
                        aligned_image = cv2.warpAffine(frame,transformation_matrix[0],(112,112))
                        embedding = recognitionService.recognize_face(aligned_image)
                        p_list = embedding.tolist()
                        identity_id = input("identity_id: ")
                        #wait for async function on event loop
                        future = asyncio.run_coroutine_threadsafe(databaseManager.add(Embedding(identity_id=identity_id,vector=p_list)),self.loop)
                        embedding_obj = future.result()
                        print(f"added: {embedding_obj}")
                        input("type to continue")
            except Exception as e:
                traceback.print_exc()
                print(e)
            finally:
                self.cap.release()

    #def insert_identities(self):
    #    LFW = "./lfw"
    #    TRACKER_FILE = "tracker.json"
    #   MIN_IMAGES = 2
    #    while self.thread_running:
    #        try:
                #fetch faces


recognitionService = RecognitionService(True)