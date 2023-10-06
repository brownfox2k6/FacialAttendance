# ./recognize.py

from cv2 import COLOR_BGR2RGB, cvtColor
from numpy import ndarray
from PyQt6 import QtCore
from PyQt6.QtCore import QMetaObject, Qt, QThread, pyqtSlot
from PyQt6.QtGui import QIcon, QImage, QPixmap
from PyQt6.QtWidgets import (QApplication, QGroupBox, QLabel, QMainWindow,
                             QVBoxLayout)
from qdarktheme import load_stylesheet, setup_theme

from db_access.attendance_repository import AttendanceRepository
from init import UI
from threads.recognize_thread import RecognizeThread
from threads.webcam_thread import WebcamThread


class RecognizeWindow(QMainWindow, UI):
    def __init__(self):
        super().__init__()
        setup_theme('auto')

        if load_stylesheet('dark')[:30] == load_stylesheet('auto')[:30]:
            self.qlabel_ss = 'padding-left: 5px; border: 1px solid rgb(63, 64, 66);'
        else:
            self.qlabel_ss = 'padding-left: 5px; border: 1px solid rgb(218, 220, 224);'

        self.setObjectName('recognizeWindow')
        self.setWindowIcon(QIcon(f'./resources/facercg.png'))
        self.setWindowTitle(self.trans('Attendance check'))
        self.setMinimumSize(720, 410)
        self.setMaximumSize(720, 410)

        self.group_box = QGroupBox(self)
        self.group_box.setGeometry(20, 20, 360, 320)
        self.group_box.setStyleSheet('font-size: 16pt;')
        self.group_box.setTitle(self.trans('Student information'))

        self.bb = QVBoxLayout(self.group_box)
        self.bb.setSpacing(0)

        self.name1 = QLabel()
        self.name1.setFixedHeight(35)
        self.name1.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.name1.setStyleSheet('font-size: 11pt;')
        self.name1.setText(self.trans('Full name'))
        self.id1 = QLabel()
        self.id1.setFixedHeight(25)
        self.id1.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.id1.setStyleSheet('font-size: 11pt;')
        self.id1.setText(self.trans('Student ID'))
        self.class1 = QLabel()
        self.class1.setFixedHeight(25)
        self.class1.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.class1.setStyleSheet('font-size: 11pt;')
        self.class1.setText(self.trans('Class'))
        self.status1 = QLabel()
        self.status1.setFixedHeight(25)
        self.status1.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.status1.setStyleSheet('font-size: 11pt;')
        self.status1.setText(self.trans('Status'))

        self.name2 = QLabel()
        self.name2.setStyleSheet(self.qlabel_ss)
        self.id2 = QLabel()
        self.id2.setStyleSheet(self.qlabel_ss)
        self.class2 = QLabel()
        self.class2.setStyleSheet(self.qlabel_ss)
        self.status2 = QLabel()
        self.status2.setStyleSheet(self.qlabel_ss)

        self.bb.addWidget(self.name1)
        self.bb.addWidget(self.name2)
        self.bb.addWidget(self.id1)
        self.bb.addWidget(self.id2)
        self.bb.addWidget(self.class1)
        self.bb.addWidget(self.class2)
        self.bb.addWidget(self.status1)
        self.bb.addWidget(self.status2)

        self.frame_label = QLabel(self)
        self.frame_label.setGeometry(400, 35, 300, 300)

        self.guide_label = QLabel(self)
        self.guide_label.setGeometry(20, 350, 680, 50)
        self.guide_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.recognize = RecognizeThread()
        self.recognize.signal.connect(self.update_status)
        self.recognize.bbox_signal.connect(self.update_bboxes)
        self.recognize_thread = QThread()
        self.recognize.moveToThread(self.recognize_thread)
        self.recognize_thread.start()

        self.webcam_thread = WebcamThread()
        self.webcam_thread.frame_to_display_signal.connect(self.display_frame)
        self.webcam_thread.frame_to_process_signal.connect(
            self.recognize.process)
        self.webcam_thread.start()

        self.attendanceRepository = AttendanceRepository()
        self.bboxes = ()
        self.bbox_color = 'yellow'

        QMetaObject.connectSlotsByName(self)

    @pyqtSlot(ndarray)
    def display_frame(self, frame):
        for x, y, w, h in self.bboxes:
            self.rounded_rect(frame, (x, y), (x+w, y+h), self.bbox_color)
        frame = cvtColor(frame, COLOR_BGR2RGB)
        h, w, ch = frame.shape
        qimg = QImage(frame.data, w, h, ch*w, QImage.Format.Format_RGB888)
        self.frame_label.setPixmap(QPixmap.fromImage(qimg))

    @pyqtSlot(tuple)
    def update_status(self, status):
        match status[0]:
            case 'NOT VALID':
                self.bbox_color = 'yellow'
                self.guide_label.setStyleSheet(
                    'font-size: 14pt; color: rgb(255, 209, 77);')
                self.guide_label.setText(
                    self.trans('There must be exactly one face in the frame'))
            case 'FAILED':
                self.bbox_color = 'red'
                self.guide_label.setStyleSheet(
                    'font-size: 14pt; color: rgb(213, 52, 87);')
                self.guide_label.setText(self.trans(
                    'Recognition failed, please try again'))
            case _:
                self.bbox_color = 'green'
                self.guide_label.setStyleSheet(
                    'font-size: 14pt; color: rgb(140, 152, 87);')
                self.guide_label.setText(
                    self.trans('Recognized successfully!'))
        self.display_student_info(status)

    @pyqtSlot(tuple)
    def update_bboxes(self, bboxes):
        self.bboxes = bboxes

    def display_student_info(self, signal):
        if len(signal) == 1:
            self.name2.setText('-')
            self.id2.setText('-')
            self.class2.setText('-')
            self.status2.setStyleSheet(self.qlabel_ss)
            self.status2.setText('-')
            return
        student_name, student_id, class_name = signal
        self.name2.setText(student_name)
        self.id2.setText(student_id)
        self.class2.setText(class_name)
        status = self.attendanceRepository.get_student_status(student_id)
        if status == 'On time':
            self.status2.setStyleSheet(
                self.qlabel_ss + 'color: rgb(140, 152, 87)')
            self.status2.setText(self.trans('On time'))
        else:
            self.status2.setStyleSheet(
                self.qlabel_ss + 'color: rgb(213, 52, 87)')
            self.status2.setText(self.trans('Late'))


if __name__ == '__main__':
    from sys import argv
    from PyQt6.QtWidgets import QApplication

    app = QApplication(argv)
    window = RecognizeWindow()
    window.show()
    app.exec()
