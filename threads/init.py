from json import load
from cv2 import (FaceDetectorYN, FaceRecognizerSF, FaceRecognizerSF_FR_COSINE,
                 FaceRecognizerSF_FR_NORM_L2)
from numpy import int32


class FaceProcess:
    def __init__(self):
        self.load_configurations()
        self.init_detector()
        self.init_recognizer()

    def load_configurations(self):
        with open(f"./resources/configurations.json") as configurations:
            data = load(configurations)
            self.face_detection_model = data["face_detection_model"]
            self.face_recognition_model = data["face_recognition_model"]
            self.similarity_metric = data["similarity_metric"]
            self.cosine_similarity_threshold = data["cosine_similarity_threshold"]
            self.l2_similarity_threshold = data["l2_similarity_threshold"]
            self.register_frames_limit = data["register_frames_limit"]
            del data

    def init_detector(self):
        self.detector = FaceDetectorYN.create(
            model=self.face_detection_model,
            config="",
            input_size=(300, 300),
            score_threshold=0.9,
            nms_threshold=0.3,
            top_k=5000
        )

    def init_recognizer(self):
        self.recognizer = FaceRecognizerSF.create(
            model=self.face_recognition_model,
            config=""
        )

    def get_bboxes(self, faces):
        if faces is None:
            return tuple()
        return tuple(map(lambda face: face[:4].astype(int32), faces))

    def get_feature(self, frame, face):
        face_align = self.recognizer.alignCrop(frame, face)
        face_feature = self.recognizer.feature(face_align)
        return face_feature

    def compare(self, f1, f2):
        match self.similarity_metric:
            case "cosine":
                cosine_score = self.recognizer.match(f1, f2, FaceRecognizerSF_FR_COSINE)
                return cosine_score >= self.cosine_similarity_threshold
            case "l2":
                l2_score = self.recognizer.match(f1, f2, FaceRecognizerSF_FR_NORM_L2)
                return l2_score <= self.l2_similarity_threshold
            case _:
                raise ValueError("similarity metric is not 'cosine' or 'l2'")
