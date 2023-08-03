import pickle

import face_recognition
import numpy
from PyQt6 import QtCore

import constants


class RegisterThread(QtCore.QThread):
    register_signal = QtCore.pyqtSignal(str)

    def __init__(self, student_id):
        super().__init__()
        self.register_progress = 0
        self.known_encodings = []
        self.status = None
        self.id = student_id
    
    @QtCore.pyqtSlot(numpy.ndarray)
    def run(self, frame):
        while self.register_progress < constants.NUM_ENCODE_IMG:
            face_locations = face_recognition.face_locations(frame, model=constants.FACE_LOCATIONS_MODEL)
            if not face_locations:
                self.status = "NO_FACE"
                continue
            elif len(face_locations) > 1:
                self.status = "MORE_THAN_ONE_FACE"
                continue
            face_encoding = face_recognition.face_encodings(frame, face_locations)[0]

        if not any(face_recognition.compare_faces(self.known_encodings, face_encoding, constants.REGISTER_FACES_TOLERANCE)):
            self.known_encodings.append(face_encoding)
            self.register_progress += 1

        file_path = f"{constants.ENCODING_FOLDER_PATH}/{self.id}.tmp"
        data = {"encodings": self.known_encodings, "ids": [self.id]*constants.NUM_ENCODE_IMG}
        with open(file_path, "wb") as temporary_encode_file:
            temporary_encode_file.write(pickle.dumps(data))

        self.register_signal.emit(file_path)
