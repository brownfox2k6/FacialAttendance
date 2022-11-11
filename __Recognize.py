from datetime import date, datetime
from os.path import join
from queue import Queue
from constants import DATABASE_FILE_PATH, NUM_RECOGNIZE_IMG, RESOURCE_FOLDER
from db_access.attendance_repository import AttendanceRepository
from db_access.class_repository import ClassRepository
from db_access.entities import AttendanceEntity
from db_access.student_repository import StudentRepository
from image_widget import ImageWidget
from numpy import ndarray
from PyQt5.QtCore import (QCoreApplication, QMetaObject, QRect, QSize, Qt,
                          pyqtSlot)
from PyQt5.QtGui import QFont, QIcon, QImage
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import (QLabel, QMainWindow, QMenuBar, QMessageBox,
                             QTableView, QWidget)
from recognize_face import RecognizeFace
from table_model import TableModel
from webcam import WebcamHandler
from sys import argv, exit
from PyQt5.QtWidgets import QApplication


class StudentRecognizeMainWindowUI(object):
    def __init__(self):
        with open(join(RESOURCE_FOLDER, "theme.txt")) as specifiedTheme:
            self.theme = "light" if specifiedTheme.read() == "1" else "dark"

    def setupUi(self, mainWindow):
        with open(join(RESOURCE_FOLDER, self.theme + ".qss")) as themeFile:
            self.styleSheet = themeFile.read()

        mainWindow.setObjectName("mainWindow")
        mainWindow.resize(940, 420)
        mainWindow.setStyleSheet(self.styleSheet)
        mainWindow.setMinimumSize(QSize(940, 420))
        mainWindow.setMaximumSize(QSize(940, 420))
        mainWindow.setWindowIcon(QIcon(join(RESOURCE_FOLDER, "facercg.png")))

        font = QFont()
        font.setPointSize(10)
        mainWindow.setFont(font)
        self.centralwidget = QWidget(mainWindow)
        self.centralwidget.setObjectName("centralwidget")
        mainWindow.setCentralWidget(self.centralwidget)

        self.imgWidget = ImageWidget(self.centralwidget)
        self.imgWidget.setGeometry(QRect(10, 10, 300, 300))
        self.imgWidget.setMinimumSize(QSize(300, 300))
        self.imgWidget.setMaximumSize(QSize(300, 300))
        self.imgWidget.setImage(QImage(join(RESOURCE_FOLDER, "facercg.png")))
        self.imgWidget.setObjectName("widget")

        self.attendanceTable = QTableView(self.centralwidget)
        self.attendanceTable.setGeometry(QRect(330, 10, 600, 300))
        self.attendanceTable.setMinimumSize(QSize(600, 300))
        self.attendanceTable.setMaximumSize(QSize(600, 300))
        self.attendanceTable.setObjectName("tableView")

        self.guideLabel = QLabel(self.centralwidget)
        self.guideLabel.setGeometry(QRect(0, 320, 940, 70))
        self.guideLabel.setMinimumSize(QSize(940, 70))
        self.guideLabel.setMaximumSize(QSize(940, 70))
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.guideLabel.setFont(font)
        self.guideLabel.setAlignment(Qt.AlignCenter)
        self.guideLabel.setObjectName("label")

        self.menubar = QMenuBar(mainWindow)
        self.menubar.setGeometry(QRect(0, 0, 633, 23))
        self.menubar.setObjectName("menubar")
        mainWindow.setMenuBar(self.menubar)

        self.retranslateUi(mainWindow)
        QMetaObject.connectSlotsByName(mainWindow)

    def retranslateUi(self, mainWindow):
        _translate = QCoreApplication.translate
        mainWindow.setWindowTitle(_translate("mainWindow", "Điểm danh học sinh"))
        self.guideLabel.setText(_translate("mainWindow", ""))


class StudentRecognizeMainWindow(QMainWindow, StudentRecognizeMainWindowUI):
    def __init__(self):
        super().__init__(None)
        self.setupUi(self)
        # Hiển thị khi camera chưa được hiện lên
        self.guideLabel.setText("Vui lòng chờ... Camera đang khởi động...")

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

        self.attendanceModel = []
        self.attendanceTableHeader = ("Họ và Tên", "Mã học sinh", "Lớp", "Thời gian điểm danh")
        self.attendanceTableModel = TableModel(self.attendanceModel, self.attendanceTableHeader)
        self.attendanceTable.setModel(self.attendanceTableModel)
        self.attendanceTable.setColumnWidth(0, 210)
        self.attendanceTable.setColumnWidth(1, 110)
        self.attendanceTable.setColumnWidth(2, 65)
        self.attendanceTable.setColumnWidth(3, 164)

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
        # Khi hasDfoneFaceRecognition = False, tức là chưa hoàn thành
        # thuật toán nhận diện khuôn mặt thì vẫn hiển thị hướng dẫn
        if self.hasDoneFaceRecognition == False:
            self.guideLabel.setText("Định vị khuôn mặt của bạn vào giữa khung hình\nTiến độ: {}/{}"
                                    .format(self.recognizeFace.attemptCount, NUM_RECOGNIZE_IMG))

        # Hiển thị khung hình lên giao diện chương trình
        self.display_image(image, self.imgWidget) 

        # Add vào queue
        self.image_queue.put(image)

    @pyqtSlot(str, str)
    def recognizeCallback(self, result, student_id):
        if result == "NoFace":
            self.hasDoneFaceRecognition = False
            self.guideLabel.setStyleSheet(self.styleSheet)

        else:
            self.hasDoneFaceRecognition = True

            if result == "Fail":
                self.playFailSound.play()
                self.guideLabel.setStyleSheet(self.failLabelStylesheet)
                self.guideLabel.setText("Nhận dạng thất bại, vui lòng thử lại")

            elif result == "MoreThanOneFace":
                self.playFailSound.play()
                self.guideLabel.setStyleSheet(self.failLabelStylesheet)
                self.guideLabel.setText("Có nhiều hơn một khuôn mặt trong khung hình")

            # result = "Success"
            else:
                # Lấy ra mã học sinh và lớp
                students = self.studentRepository.get_by_student_id(student_id)
                if len(students) > 0:
                    classes = self.classRepository.get_class(students[0].class_id)
                    if len(classes) > 0:
                        class_name = classes[0].name

                    # Lưu vào database điểm danh nếu học sinh chưa điểm danh trong ngày
                    if not self.attendanceRepository.check_student_attendance(student_id, self.today):
                        self.playSuccessSound.play()
                        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        self.attendanceRepository.add_attendance(AttendanceEntity(None, self.today, students[0].student_id, now, None))
                        # show to list
                        self.attendanceModel.insert(0, (students[0].name, student_id, class_name, now))
                        self.attendanceTable.model().layoutChanged.emit()

                    # Hiển thị thông báo nhận diện thành công và hiển thị tên + mã hs + lớp
                    self.guideLabel.setStyleSheet(self.successLabelStylesheet)
                    self.guideLabel.setText("Nhận diện thành công\n" + students[0].name + " - " + students[0].student_id + " - " + class_name)

                else:
                    self.playFailSound.play()
                    self.guideLabel.setStyleSheet(self.failLabelStylesheet)
                    self.guideLabel.setText("Không tìm thấy thông tin học sinh")

        # Clear queue
        with self.image_queue.mutex:
            self.image_queue.queue.clear()

    # Hàm hiển thị webcam trên giao diện chương trình
    def display_image(self, img, display):
        h, w, ch = img.shape
        bytes_per_line = ch * w
        display.setImage(QImage(img.data, h, w, bytes_per_line, QImage.Format_RGB888))

    # Hàm thực hiện khi kích chuột nút thoát chương trình
    def closeEvent(self, event):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText("Bạn có muốn thoát chương trình hay không?")
        msg.setWindowTitle("Xác nhận lại")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        result = msg.exec()
        if result == QMessageBox.Yes:
            self.webcamHandler.stop()
            self.recognizeFace.stop()
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(argv)
    mainWindow = StudentRecognizeMainWindow()
    mainWindow.show()
    exit(app.exec_())