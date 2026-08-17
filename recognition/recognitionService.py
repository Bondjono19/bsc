import cv2
import numpy as np
import time,csv
import os
import json
from cv2.typing import MatLike
import onnxruntime as oxrt
import asyncio
import traceback
from recognition.utils.get_points import get_reference_points
from shared.database.databaseManager import DatabaseManager
from shared.database.models import Identity,Embedding, Event
from recognition.eventConnectionService import EventConnectionService
from recognition.accessGrantor import AccessGrantor
from skimage.transform import SimilarityTransform
from datasets import load_dataset

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
TEST_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils/data")
GALLERY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils", "data/gallery.txt")
PROBES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),"utils","data/probes.txt")
VALID_NAMES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),"utils","data/unique_gallery_names.txt")
RESULTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),"utils","data/results.csv")
BROKER_LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),"utils","data/sent_events_broker_test.csv")
T_8_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),"utils","data/t_8_results.csv")
T_OFFLINE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),"utils","data/sent_events_offline_test.csv")
class RecognitionService:
    def __init__(self, mode: bool,access_grantor: AccessGrantor,database_manager: DatabaseManager, eventConnectionService: EventConnectionService):
        self.mode = mode
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
        self.accessGrantor = access_grantor
        self.databaseManager = database_manager
        self.eventConnectionService = eventConnectionService
        self.t2_results = open(os.path.join(TEST_DATA_PATH,"t2_results.csv"), "w", newline="")
        self.t8_results = open(T_8_PATH,"w",newline="")
        self.offline_results = open(T_OFFLINE_PATH,"w",newline="")
        self.log = csv.writer((self.t2_results))
        self.log.writerow(["timestamp","detect_ms","align_ms","embed_ms","compare_ms","total_ms"])
        self.results_broker_test = open(BROKER_LOG_PATH, "w", newline="")
        self.log_broker_test = csv.writer((self.results_broker_test))
        self.log_broker_test.writerow(["timestamp","content","channel"])
        self.log_t8 = csv.writer((self.t8_results))
        self.log_t8.writerow(["timestamp","iteration_ms"])
        self.log_offline_test = csv.writer((self.offline_results))
        self.log_offline_test.writerow(["timestamp", "event"])

    async def __aenter__(self):
        self.detector = cv2.FaceDetectorYN.create(os.path.join(MODELS_DIR, "face_detection_yunet_2023mar.onnx"),"",self.camera_dimensions)
        self.detector.setInputSize((640,480))
        self.recognizer = oxrt.InferenceSession(os.path.join(MODELS_DIR, "edgeface_xs_gamme_06.onnx"),providers=["CPUExecutionProvider"])
        self.reference_points = np.asarray(get_reference_points(),dtype=np.float32).reshape(5,2)
        self.identities = []
        self.loop = asyncio.get_running_loop()
        await self.load_identites()
        self.thread_running = True
        match self.mode:
            case "DETECTION_MODE":
                self.thread = asyncio.create_task(asyncio.to_thread(self.detect_face))
            case "GALLERY_INSERTION_MODE":
                self.thread = asyncio.create_task(asyncio.to_thread(self.insert_gallery))
            case "RUN_PROBES_MODE":
                self.thread = asyncio.create_task(asyncio.to_thread(self.run_probes))
            case "BROKER_TEST_MODE":
                self.thread = asyncio.create_task(asyncio.to_thread(self.detect_face_broker_test))
            case "T8_TEST_MODE":
                self.thread = asyncio.create_task(asyncio.to_thread(self.detect_face_t8))
            case "OFFLINE_MODE":
                self.thread = asyncio.create_task(asyncio.to_thread(self.detect_face_offline_test))
            case _:
                self.thread = asyncio.create_task(asyncio.to_thread(self.detect_face))
        return self
    
    async def load_identites(self):
        identities = await self.databaseManager.fetchAll(Identity, Identity.embeddings)
        if identities is not None:
            for identity in identities:
                embeddings = identity.embeddings
                for embedding in embeddings:
                    vector = np.asarray(embedding.vector,dtype=np.float32)
                    self.identities.append((identity.id,identity.global_id,identity.name,vector))
        print(f"Loaded {len(self.identities)} identity embeddings")

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
                    #h,w, _ = frame.shape
                    if not (self.cap.isOpened()):
                        print("broke loop, cap not open")
                        break
                    if not ret:
                        print("no ret")
                        break
                    t_0 = time.perf_counter()
                    #self.detector.setInputSize((w,h))
                    _, faces = self.detector.detect(frame)
                    t_1 = time.perf_counter()
                    print(faces)
                    if faces is not None:
                        if len(faces) > 1:
                            print("More than one face detected - skipping")
                            continue
                        for face in faces:
                            landmarks = face[4:14].reshape(5,2).astype(np.float32)
                            transformation_matrix = SimilarityTransform.from_estimate(landmarks,self.reference_points)#cv2.estimateAffinePartial2D(landmarks,self.reference_points)
                            aligned_image = cv2.warpAffine(frame,transformation_matrix.params[0:2, :],(112,112))
                            t_2 = time.perf_counter()
                            embedding = self.recognize_face(aligned_image)
                            t_3 = time.perf_counter()
                            result = self.compare_faces(np.asarray(embedding,dtype=np.float32).flatten())
                            t_4 = time.perf_counter()
                            response: str
                            access = result[0]>self.threshold
                            if(access):
                                response = f"Detected: {result[1][2]} with local id {result[1][0]} at {result[0]} similarity score"
                                print(response)
                            else:
                                response = f"Face detected, no match in DB, max sim score: {result[0]}"
                                print(response)
                            #"timestamp","detect_ms","align_ms","embed_ms","compare_ms","total_ms"
                            self.log.writerow([
                                time.time(),
                                (t_1-t_0) * 1000,
                                (t_2-t_1) * 1000,
                                (t_3-t_2) * 1000,
                                (t_4-t_3) * 1000,
                                (t_4-t_0) * 1000,
                            ])
                            #fire and forget event
                            asyncio.run_coroutine_threadsafe(self.eventConnectionService.publish(Event(direction="outbound",content=response, channel=self.eventConnectionService.channel,status="pending")),self.loop)
            
                            if(access):
                                #call child class that implements grantAccess interface and pass optional data. Here name for instance.
                                self.accessGrantor.grantAccess(result[1][2])
                            
                except Exception as e:
                    print(e)
                    continue
        except Exception as e:
            print(e)
            self.thread_running = False
        finally:
            if(self.cap.isOpened()):
                self.cap.release()

    def detect_face_broker_test(self):
            try:
                id_ite = 0
                self.cap = cv2.VideoCapture(0,cv2.CAP_V4L2)
                while self.thread_running:
                    try:
                        if not self.cap.isOpened():
                            print("No cam found")
                            break
                        #print("watching")
                        ret, frame = self.cap.read()
                        #h,w, _ = frame.shape
                        if not (self.cap.isOpened()):
                            print("broke loop, cap not open")
                            break
                        if not ret:
                            print("no ret")
                            break
                        #self.detector.setInputSize((w,h))
                        _, faces = self.detector.detect(frame)
                        #print(faces)
                        if faces is not None:
                            if len(faces) > 1:
                                print("More than one face detected - skipping")
                                continue
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
                                response+= f" ID: {id_ite}"
                                asyncio.run_coroutine_threadsafe(self.eventConnectionService.publish(Event(direction="outbound",content=response, channel=self.eventConnectionService.channel,status="pending")),self.loop)
                                print(f"wrote 1 row")
                                self.log_broker_test.writerow([time.time(),response,self.eventConnectionService.channel])
                                if(access):
                                    #call child class that implements grantAccess interface and pass optional data. Here name for instance.
                                    self.accessGrantor.grantAccess(result[1][2])
                                id_ite+=1
                    except Exception as e:
                        print(e)
                        continue
            except Exception as e:
                print(e)
                self.thread_running = False
            finally:
                if(self.cap.isOpened()):
                    self.cap.release()

    def detect_face_offline_test(self):
                try:
                    id_ite = 0
                    self.cap = cv2.VideoCapture(0,cv2.CAP_V4L2)
                    while self.thread_running:
                        try:
                            if not self.cap.isOpened():
                                print("No cam found")
                                break
                            #print("watching")
                            ret, frame = self.cap.read()
                            #h,w, _ = frame.shape
                            if not (self.cap.isOpened()):
                                print("broke loop, cap not open")
                                break
                            if not ret:
                                print("no ret")
                                break
                            #self.detector.setInputSize((w,h))
                            _, faces = self.detector.detect(frame)
                            #print(faces)
                            if faces is not None:
                                if len(faces) > 1:
                                    print("More than one face detected - skipping")
                                    continue
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
                                    response+= f" LOG_ID: {id_ite}"
                                    asyncio.run_coroutine_threadsafe(self.eventConnectionService.publish(Event(direction="outbound",content=response, channel=self.eventConnectionService.channel,status="pending")),self.loop)
                                    print(f"wrote 1 row")
                                    self.log_offline_test.writerow([time.time(),response,self.eventConnectionService.channel])
                                    if(access):
                                        #call child class that implements grantAccess interface and pass optional data. Here name for instance.
                                        self.accessGrantor.grantAccess(result[1][2])
                                    id_ite+=1
                        except Exception as e:
                            print(e)
                            continue
                except Exception as e:
                    print(e)
                    self.thread_running = False
                finally:
                    if(self.cap.isOpened()):
                        self.cap.release()

    def detect_face_t8(self):
            try:
                self.cap = cv2.VideoCapture(0,cv2.CAP_V4L2)
                while self.thread_running:
                    try:
                        t_0 = time.perf_counter()
                        if not self.cap.isOpened():
                            print("No cam found")
                            break
                        print("watching")
                        ret, frame = self.cap.read()
                        #h,w, _ = frame.shape
                        if not (self.cap.isOpened()):
                            print("broke loop, cap not open")
                            break
                        if not ret:
                            print("no ret")
                            break
                        #self.detector.setInputSize((w,h))
                        _, faces = self.detector.detect(frame)
                        print(faces)
                        t_1 = time.perf_counter()
                        #"timestamp","iteration_ms"
                        self.log_t8.writerow([
                            time.time(),
                            (t_1-t_0)*1000,
                        ])
                        if faces is not None:
                            if len(faces) > 1:
                                print("More than one face detected - skipping")
                                continue
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
                                asyncio.run_coroutine_threadsafe(self.eventConnectionService.publish(Event(direction="outbound",content=response, channel=self.eventConnectionService.channel,status="pending")),self.loop)
                
                                if(access):
                                    #call child class that implements grantAccess interface and pass optional data. Here name for instance.
                                    self.accessGrantor.grantAccess(result[1][2])   
                    except Exception as e:
                        print(e)
                        continue
            except Exception as e:
                print(e)
                self.thread_running = False
            finally:
                if(self.cap.isOpened()):
                    self.cap.release()

    def insert_gallery(self):
        print("running gal")
        with open(GALLERY_PATH,"r") as f:
            filenames = [line.strip() for line in f]
        print("downloading dataset")
        dataset = load_dataset("bitmind/lfw")
        print("done")
        data = dataset["train"]
        images = {x["filename"]: x["image"] for x in data}
        print("started insertion")
        try:
                for filename in filenames:
                    image = images[filename]
                    cv_img = np.array(image)
                    cv_img = cv2.cvtColor(cv_img,cv2.COLOR_RGB2BGR)
                    h,w,_ = cv_img.shape
                    self.detector.setInputSize((w,h))
                    _, faces = self.detector.detect(cv_img)
                    if faces is not None:
                        if len(faces)>1:
                            print("more than 1 face - skipping")
                            continue
                        for face in faces:
                            landmarks = face[4:14].reshape(5,2).astype(np.float32)
                            transformation_matrix = SimilarityTransform.from_estimate(landmarks,self.reference_points)
                            aligned_image = cv2.warpAffine(cv_img,transformation_matrix.params[0:2, :],(112,112))
                            embedding = self.recognize_face(aligned_image)
                            stripped_name = "_".join(filename.split("_")[:-1])
                            future = asyncio.run_coroutine_threadsafe(
                                self.databaseManager.add_embedding(stripped_name, embedding.tolist()),
                                self.loop
                            )
                            future.result()
                            print(f"inserted{stripped_name} with some embedding")
        except Exception as e:
            print(e)
            raise

    def run_probes(self):
        print("Running probes")
        with open(PROBES_PATH,"r") as f:
            filenames = [line.strip() for line in f]
        with open(VALID_NAMES_PATH,"r") as f:
            valid_names = [line.strip() for line in f]
        print("downloading dataset")
        dataset = load_dataset("bitmind/lfw")
        print("done")
        data = dataset["train"]
        images = {x["filename"]: x["image"] for x in data}
        while self.thread_running:
            print("started running probes")
            try:
                with open(RESULTS_PATH,"w") as f:
                    f.write("score,pred_identity,true_identity_of_probe,is_enrolled\n")
                    for filename in filenames:
                        if not "Zidane" in filename:
                            continue
                        image = images[filename]
                        cv_img = np.array(image)
                        cv_img = cv2.cvtColor(cv_img,cv2.COLOR_RGB2BGR)
                        h,w,_ = cv_img.shape
                        debug_frame = cv_img.copy()
                        self.detector.setInputSize((w,h))
                        _, faces = self.detector.detect(cv_img)
                        if faces is not None:
                            if len(faces)>1:
                                print("len of faces more than 1 - skipping")
                                continue
                            for face in faces:
                                landmarks = face[4:14].reshape(5,2).astype(np.float32)
                                bbox = face[0:4].astype(int)
                                cv2.rectangle(debug_frame, (bbox[0], bbox[1]), (bbox[0]+bbox[2], bbox[1]+bbox[3]), (255, 0, 0), 2)
                                for (x, y) in landmarks:
                                    cv2.circle(debug_frame, (int(x), int(y)), 4, (0, 0, 255), -1)
                                transformation_matrix = SimilarityTransform.from_estimate(landmarks,self.reference_points)
                                aligned_image = cv2.warpAffine(cv_img,transformation_matrix.params[0:2, :],(112,112))
                                embedding = self.recognize_face(aligned_image)
                                result = self.compare_faces(np.asarray(embedding,dtype=np.float32).flatten())
                                stripped_probe_name = "_".join(filename.split("_")[:-1])
                                if(stripped_probe_name in valid_names):
                                    is_enrolled = True
                                else:
                                    is_enrolled = False
                                print(f"Predicted:   Max sim score: {result[0]} and predicted identity: {result[1][2]}. True identity of probe: {stripped_probe_name}. Probe is enrolled: {is_enrolled}")
                                f.write(f"{result[0]},{result[1][2]},{stripped_probe_name},{is_enrolled}"+"\n")
                                cv2.imwrite("/app/recognition/utils/data/detectedz.png", debug_frame)
                                cv2.imwrite("/app/recognition/utils/data/alignedz.png", aligned_image)
            except Exception as e:
                print(e)
            self.thread_running = False   