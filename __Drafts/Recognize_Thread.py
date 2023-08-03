import os
import pickle

import face_recognition
import numpy
from PyQt6 import QtCore

import constants


class RecognizeThread(QtCore.QThread):
    recognized_signal = QtCore.pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.attempt_count = 0
        self.is_loading_finished = False
        self.load_data()
        self.known_encodings = []
        self.known_ids = []
        self.recognized_ids = []
        self.status = None

    def load_data(self):
        for file in os.listdir(constants.ENCODING_FOLDER_PATH):
            if not file.endswith(".pkl"):
                continue
            with open(f"{constants.ENCODING_FOLDER_PATH}/{file}", "rb") as encode_file:
                data = pickle.loads(bytes(encode_file.read()))
            self.known_encodings.extend(data["encodings"])
            self.known_ids.extend(data["ids"])
        self.is_loading_finished = True

    def recognize(self, frame):
        face_locations = face_recognition.face_locations(frame, model=constants.FACE_LOCATIONS_MODEL)
        if not face_locations:
            self.recognized_ids.append(-1)
            return
        self.recognized_ids.clear()
        for face_encoding in face_recognition.face_encodings(self.frame, face_locations):
            face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)
            index_min_distance = numpy.argmin(face_distances)
            if face_distances[index_min_distance] <= constants.RECOGNIZE_FACES_TOLERANCE:
                self.recognized_ids.append(self.known_ids[index_min_distance])

    @QtCore.pyqtSlot(numpy.ndarray)
    def run(self, frame):
        while self.isRunning():
            self.recognize(frame)
            self.status = "FAIL" if not self.recognized_ids else "NO_FACE" if self.recognized_ids[0] == -1 else "SUCCESS"
            if self.status != "FAIL" or self.attempt_count > constants.NUM_RECOGNIZE_IMG:
                self.attempt_count = 0
                self.recognized_signal.emit(self.recognized_ids)
            self.attempt_count += 1
