from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from threads.init import FaceProcess
from os import listdir
from pickle import load
from numpy import ndarray

from db_access.student_repository import StudentRepository
from db_access.attendance_repository import AttendanceRepository

class RecognizeThread(QObject, FaceProcess):
    bbox_signal = pyqtSignal(tuple)
    signal = pyqtSignal(tuple)

    def __init__(self):
        super().__init__()
        self.faces_db = []
        self.memo = []
        self.attendanceRepository = AttendanceRepository()
        self.studentRepository = StudentRepository()
        self.load_data()

    def load_data(self):
        for f in filter(lambda x: x.endswith(".pkl"),
                        listdir("./database/faces_data")):
            with open(f"./database/faces_data/{f}", "rb") as file:
                faces = load(file)
            self.faces_db.extend(map(lambda face: (face, f[:-4]), faces))

    @pyqtSlot(ndarray)
    def process(self, frame):
        faces = self.detector.detect(frame)[1]
        bboxes = self.get_bboxes(faces)
        self.bbox_signal.emit(bboxes)
        if len(bboxes) != 1:
            self.signal.emit(("NOT VALID", ))
            return
        f1 = self.get_feature(frame, faces[0])
        for f2, student_id in self.memo:
            if self.compare(f1, f2):
                self.emit_student(student_id)
                return
        for f2, student_id in self.faces_db:
            if self.compare(f1, f2):
                self.emit_student(student_id)
                self.memo.append((f1, student_id))
                self.attendanceRepository.add_attendance(student_id)
                return
        self.signal.emit(("FAILED", ))

    def emit_student(self, student_id):
        """
        Emit student_name, student_id and class_name
        """
        student = self.studentRepository.get_student(student_id)[0]
        self.signal.emit((student.student_name, student.student_id,
                          student.class_name))
