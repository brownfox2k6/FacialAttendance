# ./threads/register_thread.py

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from threads.init import FaceProcess
from numpy import ndarray
from pickle import dump

from db_access.student_repository import StudentRepository


class RegisterThread(QObject, FaceProcess):
    bbox_signal = pyqtSignal(tuple)
    signal = pyqtSignal(str)

    def __init__(self, student):
        super().__init__()
        self.known_faces = []
        self.counter = 0
        self.studentRepository = StudentRepository()
        self.student = student

    def inc_counter(self):
        self.counter += 1
        self.signal.emit(str(self.counter))

    @pyqtSlot(ndarray)
    def process(self, frame):
        faces = self.detector.detect(frame)[1]
        bboxes = self.get_bboxes(faces)
        self.bbox_signal.emit(bboxes)
        if len(bboxes) != 1:
            self.signal.emit("NOT VALID")
            return
        self.inc_counter()
        f1 = self.get_feature(frame, faces[0])
        for f2 in self.known_faces:
            if self.compare(f1, f2):
                break
        else:
            self.known_faces.append(f1)

    def save(self):
        print(len(self.known_faces))
        with open(f"./database/faces_data/{self.student.student_id}.pkl", "wb") as f:
            dump(self.known_faces, f)
        self.studentRepository.add_student(self.student)
        self.signal.emit("SAVED")
