from datetime import date, datetime
from json import load
from os.path import join
from queue import Queue
from constants import DATABASE_FILE_PATH, NUM_RECOGNIZE_IMG, RESOURCE_FOLDER
from db_access.attendance_repository import AttendanceRepository
from db_access.class_repository import ClassRepository
from db_access.entities import AttendanceEntity
from db_access.student_repository import StudentRepository
from resources.image_widget import ImageWidget
from numpy import ndarray
from PyQt5.QtCore import (QCoreApplication, QMetaObject, QRect, QSize, Qt,
                          pyqtSlot)
from PyQt5.QtGui import QFont, QIcon, QImage
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import (QLabel, QMainWindow, QMenuBar, QMessageBox,
                             QTableView, QWidget)
from recognize_face import RecognizeFace
from resources.table_model import TableModel
from webcam import WebcamHandler
from sys import argv, exit
from PyQt5.QtWidgets import QApplication
from cv2 import cvtColor, COLOR_BGR2RGB, rectangle


class StudentRecognizeMainWindowUI(object):
    def __init__(self):
        with open(join(RESOURCE_FOLDER, "translations.json"), encoding="utf-8") as translations:
            self.transdict = load(translations)
        with open(join(RESOURCE_FOLDER, "configurations.json")) as configurations:
            loaded = load(configurations)
            self.lang = loaded["lang"]
            with open(join(RESOURCE_FOLDER, loaded["theme"] + ".qss")) as themeFile:
                self.styleSheet = themeFile.read()
        self.translated = lambda x: self.transdict[self.lang][x]

    def setupUi(self, mainWindow):
        mainWindow.setObjectName("mainWindow")
        mainWindow.resize(788, 602)
        mainWindow.setStyleSheet(self.styleSheet)
        mainWindow.setMinimumSize(QSize(788, 602))
        mainWindow.setMaximumSize(QSize(788, 602))
        mainWindow.setWindowIcon(QIcon(join(RESOURCE_FOLDER, "facercg.png")))

        self.centralwidget = QWidget(mainWindow)
        self.centralwidget.setObjectName("centralwidget")
        mainWindow.setCentralWidget(self.centralwidget)

        self.imgWidget = ImageWidget(self.centralwidget)
        self.imgWidget.setGeometry(QRect(10, 10, 768, 432))
        self.imgWidget.setMaximumSize(QSize(768, 432))
        self.imgWidget.setMinimumSize(QSize(768, 432))
        self.imgWidget.setImage(QImage(join(RESOURCE_FOLDER, "facercg.png")))
        self.imgWidget.setObjectName("widget")

        self.guideLabel = QLabel(self.centralwidget)
        self.guideLabel.setGeometry(QRect(0, 452, 768, 150))
        self.guideLabel.setMinimumSize(QSize(768, 150))
        self.guideLabel.setMaximumSize(QSize(768, 150))
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.guideLabel.setFont(font)
        self.guideLabel.setAlignment(Qt.AlignCenter)
        self.guideLabel.setObjectName("label")

        self.retranslateUi(mainWindow)
        QMetaObject.connectSlotsByName(mainWindow)

    def retranslateUi(self, mainWindow):
        _translate = QCoreApplication.translate
        mainWindow.setWindowTitle(_translate("mainWindow", self.translated("Attendance check")))
        self.guideLabel.setText(_translate("mainWindow", ""))


class StudentRecognizeMainWindow(QMainWindow, StudentRecognizeMainWindowUI):
    def __init__(self):
        super().__init__(None)
        self.setupUi(self)
        self.guideLabel.setText(self.translated("Please wait... Camera is starting..."))

        self.classRepository = ClassRepository(DATABASE_FILE_PATH)
        self.studentRepository = StudentRepository(DATABASE_FILE_PATH)
        self.attendanceRepository = AttendanceRepository(DATABASE_FILE_PATH)

        self.webcamHandler = WebcamHandler()
        self.webcamHandler.imgSignal.connect(self.captureImageCallback)

        self.image_queue = Queue()
        self.recognizeFace = RecognizeFace(self.image_queue)
        self.recognizeFace.recognizedSignal.connect(self.recognizeCallback)

        self.webcamHandler.start()
        self.recognizeFace.start()

        self.playSuccessSound = QSound(join(RESOURCE_FOLDER, "recognize_success.wav"))
        self.playFailSound = QSound(join(RESOURCE_FOLDER, "recognize_fail.wav"))

        if self.theme == "light":
            self.successLabelStylesheet = "color: green"
            self.failLabelStylesheet = "color: red"
        else:
            self.successLabelStylesheet = "color: lightgreen"
            self.failLabelStylesheet = "color: rgb(255, 70, 70)"  # lightred

        self.today = date.today().strftime("%d/%m/%Y")
        self.hasDoneFaceRecognition = False


    @pyqtSlot(ndarray)
    def captureImageCallback(self, image):
        # Display instructions until finish face recognition
        if not self.hasDoneFaceRecognition:
            self.guideLabel.setText(f"{self.translated('Move your face')}\n{self.translated('Progress')}:\
                                      {self.registerFace.registerProgress}/{NUM_RECOGNIZE_IMG}")

        self.image = cvtColor(image, COLOR_BGR2RGB)

        # Display camera on UI and push in queue
        self.display_image(self.image, self.imgWidget) 
        self.image_queue.put(self.image)

    @pyqtSlot(str, list)
    def recognizeCallback(self, result, student_ids):
        if result == "NoFace":
            self.hasDoneFaceRecognition = False
            self.guideLabel.setStyleSheet(self.styleSheet)

        elif result == "Fail":
            self.hasDoneFaceRecognition = True
            self.guideLabel.setStyleSheet(self.failLabelStylesheet)
            self.playFailSound.play()
            self.guideLabel.setText(self.translated("Get samples failed. Please try again."))
        
        else:
            self.hasDoneFaceRecognition = True
            self.guideLabel.setStyleSheet(self.successLabelStylesheet)
            guideLabel_content = []

            for student_id in student_ids:
                if student_id == "Unknown":
                    self.playFailSound.play()

                # Save to attendance database if student hasn't attend before (in day)
                else:
                    student = self.studentRepository.get_by_student_id(student_id)[0]
                    if not self.attendanceRepository.check_student_attendance(student_id, self.today):
                        self.playSuccessSound.play()
                        self.attendanceRepository.add_attendance(AttendanceEntity(None, self.today, student.student_id, datetime.now().strftime("%d/%m/%Y %H:%M:%S"), None))
                    guideLabel_content.append(f"{student.name} - {student.student_id} - {self.classRepository.get_class(student.class_id)[0].name}")
                    self.guideLabel.setText("\n".join(guideLabel_content))

        # Clear queue
        with self.image_queue.mutex:
            self.image_queue.queue.clear()

    # Function: Display webcam on interface
    def display_image(self, img, display):
        h, w, ch = img.shape
        display.setImage(QImage(img.data, w, h, ch*w, QImage.Format_RGB888))

    # Function: Executes when click Exit
    def closeEvent(self, event):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText(self.translated("Do you want to exit?"))
        msg.setWindowTitle(self.translated("Reconfirm"))
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = msg.exec()
        if result == QMessageBox.Yes:
            self.webcamHandler.stop()
            self.recognizeFace.stop()
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(argv)
    mainWindow = StudentRecognizeMainWindow()
    mainWindow.show()
    exit(app.exec_())
