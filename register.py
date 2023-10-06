# ./register.py

from re import fullmatch

from cv2 import COLOR_BGR2RGB, cvtColor
from numpy import ndarray
from PyQt6.QtCore import QMetaObject, Qt, QThread, pyqtSlot
from PyQt6.QtGui import QIcon, QImage, QPixmap
from PyQt6.QtWidgets import (QFormLayout, QGroupBox, QLabel, QLineEdit,
                             QMainWindow, QMessageBox, QPushButton, QWidget)

from db_access.class_repository import ClassRepository
from db_access.entities import StudentEntity
from db_access.student_repository import StudentRepository
from init import UI
from threads.register_thread import RegisterThread
from threads.webcam_thread import WebcamThread
import qdarktheme


class RegisterWindow(QMainWindow, UI):
    def __init__(self):
        super().__init__()
        qdarktheme.setup_theme('auto')

        self.setObjectName('registerWindow')
        self.setWindowIcon(QIcon(f'./resources/facercg.png'))
        self.setWindowTitle(self.trans('Face registration'))
        self.setMinimumSize(720, 410)
        self.setMaximumSize(720, 410)

        self.group_box = QGroupBox(self)
        self.group_box.setGeometry(20, 20, 360, 281)
        self.group_box.setStyleSheet('font-size: 16pt')
        self.group_box.setTitle(self.trans('Student information'))

        self.form_layout_widget = QWidget(self.group_box)
        self.form_layout_widget.setGeometry(10, 50, 330, 216)

        self.form_layout = QFormLayout(self.form_layout_widget)
        self.form_layout.setContentsMargins(0, 0, 0, 0)
        self.form_layout.setVerticalSpacing(18)

        self.name_edit = QLineEdit(self.form_layout_widget)
        self.name_edit.setPlaceholderText(self.trans('Full name'))
        self.form_layout.setWidget(
            0, QFormLayout.ItemRole.FieldRole, self.name_edit)

        self.student_id_edit = QLineEdit(self.form_layout_widget)
        self.student_id_edit.setPlaceholderText(self.trans('Student ID'))
        self.form_layout.setWidget(
            1, QFormLayout.ItemRole.FieldRole, self.student_id_edit)

        self.class_edit = QLineEdit(self.form_layout_widget)
        self.class_edit.setPlaceholderText(self.trans('Class (e.g. 10A1)'))
        self.form_layout.setWidget(
            2, QFormLayout.ItemRole.FieldRole, self.class_edit)

        self.parent_email_edit = QLineEdit(self.form_layout_widget)
        self.parent_email_edit.setPlaceholderText(
            self.trans('Email (e.g. abc@gmail.com)'))
        self.form_layout.setWidget(
            3, QFormLayout.ItemRole.FieldRole, self.parent_email_edit)

        self.frame_label = QLabel(self)
        self.frame_label.setGeometry(400, 10, 300, 300)
        pm = QPixmap.fromImage(QImage(f'./resources/facercg.png')).scaled(
            300, 300, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self.frame_label.setPixmap(pm)

        self.guide_label = QLabel(self)
        self.guide_label.setGeometry(400, 330, 291, 61)
        self.guide_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.guide_label.setWordWrap(True)
        self.guide_label.setStyleSheet('font-size: 14pt')
        self.guide_label.setText(self.trans(
            'Enter your information then select "Get samples"'))

        self.get_sample_button = QPushButton(self)
        self.get_sample_button.setGeometry(60, 333, 130, 41)
        self.get_sample_button.setStyleSheet('font-size: 13pt')
        self.get_sample_button.setText(self.trans('Get samples'))
        self.get_sample_button.clicked.connect(self.start_registering)

        self.cancel_button = QPushButton(self)
        self.cancel_button.setGeometry(225, 333, 111, 41)
        self.cancel_button.setStyleSheet('font-size: 13pt')
        self.cancel_button.setText(self.trans('Cancel'))
        self.cancel_button.clicked.connect(self.close)

        self.studentRepository = StudentRepository()
        self.classRepository = ClassRepository()

        QMetaObject.connectSlotsByName(self)

    def check_information_error(self, student_name, student_id, class_name, parent_email):
        error = []
        if not student_id:
            error.append(self.trans('• Student ID is empty'))
        elif not student_id.isascii():
            error.append(self.trans(
                '• Student ID must contain only ASCII characters'))
        elif not student_id.isalnum():
            error.append(self.trans(
                '• Student ID must not contain spaces or special characters'))
        if not student_name:
            error.append(self.trans('• Full name is empty'))
        elif not student_name.replace(' ', '').isalpha():
            error.append(self.trans(
                '• Full name contains numerical characters or special characters'))
        if self.studentRepository.get_student(student_id):
            error.append(self.trans('• This Student ID has already exist'))
        if not self.classRepository.get_class(class_name):
            error.append(self.trans('• Invalid class name'))
        if not fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', parent_email):
            error.append(self.trans('• Invalid email'))
        return error

    def start_registering(self):
        student_name = self.name_edit.text()
        student_id = self.student_id_edit.text()
        class_name = self.class_edit.text()
        parent_email = self.parent_email_edit.text()

        error = self.check_information_error(
            student_name, student_id, class_name, parent_email)
        if error:
            ret = self.show_error_msgbox('\n'.join(error))
            return

        info = (
            self.trans('Please recheck your information carefully, then click "Yes" to start '
                       'recording face, otherwise click "No" to edit your information.'), '',
            f'• {self.trans("Full name")}: {student_name}',
            f'• {self.trans("Student ID")}: {student_id}',
            f'• {self.trans("Class")}: {class_name}',
            f'• {self.trans("Email")}: {parent_email}'
        )
        ret = self.show_yn_msgbox('\n'.join(info))
        if ret == QMessageBox.StandardButton.No:
            return

        self.register = RegisterThread(StudentEntity(
            student_id, student_name, class_name, parent_email))
        self.register.bbox_signal.connect(self.update_bboxes)
        self.register.signal.connect(self.update_status)
        self.register_thread = QThread()
        self.register.moveToThread(self.register_thread)
        self.register_thread.start()

        self.webcam_thread = WebcamThread()
        self.webcam_thread.frame_to_display_signal.connect(self.display_frame)
        self.webcam_thread.frame_to_process_signal.connect(
            self.register.process)
        self.webcam_thread.start()

        self.bboxes = tuple()
        self.get_sample_button.setEnabled(False)
        self.name_edit.setEnabled(False)
        self.student_id_edit.setEnabled(False)
        self.class_edit.setEnabled(False)
        self.parent_email_edit.setEnabled(False)

    @pyqtSlot(tuple)
    def update_bboxes(self, bboxes):
        self.bboxes = bboxes

    @pyqtSlot(ndarray)
    def display_frame(self, frame):
        for x, y, w, h in self.bboxes:
            self.rounded_rect(frame, (x, y), (x+w, y+h), 'yellow')
        frame = cvtColor(frame, COLOR_BGR2RGB)
        h, w, ch = frame.shape
        qimg = QImage(frame.data, w, h, ch*w, QImage.Format.Format_RGB888)
        self.frame_label.setPixmap(QPixmap.fromImage(qimg))

    @pyqtSlot(str)
    def update_status(self, status):
        match status:
            case 'NOT VALID':
                self.guide_label.setText(self.trans(
                    'There must be exactly one face in the frame'))
            case 'SAVED':
                self.register_thread.quit()
                self.bboxes = ()
                self.show_ok_msgbox(self.trans(
                    'Registered successfully! Click "Ok" to exit.'))
                self.close()
            case _:
                prog = int(status)
                self.guide_label.setText(f'{self.trans("Progress")}: '
                                         + f'{round(prog / self.register_frames_limit * 100, 1)}%')
                if prog == self.register_frames_limit:
                    self.register.save()
                    return


if __name__ == '__main__':
    from sys import argv
    from PyQt6.QtWidgets import QApplication

    app = QApplication(argv)
    window = RegisterWindow()
    window.show()
    app.exec()
