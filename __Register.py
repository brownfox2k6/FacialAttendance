from os import remove, rename
from os.path import exists, join
from queue import Queue
from sys import argv, exit
from PyQt5.QtWidgets import QApplication

from constants import (DATABASE_FILE_PATH, ENCODING_FOLDER_PATH,
                       NUM_ENCODE_IMG, RESOURCE_FOLDER)
from db_access.class_repository import ClassRepository
from db_access.entities import StudentEntity
from db_access.student_repository import StudentRepository
from image_widget import ImageWidget
from numpy import ndarray
from PyQt5.QtCore import (QCoreApplication, QMetaObject, QRect, QSize, Qt,
                          pyqtSlot)
from PyQt5.QtGui import QFont, QIcon, QImage
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import (QAction, QComboBox, QDateEdit, QFormLayout,
                             QGroupBox, QLabel, QLineEdit, QMainWindow, QMenu,
                             QMenuBar, QMessageBox, QPushButton, QWidget)
from register_face import RegisterFace
from registered_student_list import RegisteredStudentListDialog
from webcam import WebcamHandler


class StudentRegisterMainWindowUI(object):
    def __init__(self):
        with open(join(RESOURCE_FOLDER, "theme.txt")) as specifiedTheme:
            self.theme = "light" if specifiedTheme.read() == "1" else "dark"

    def setupUi(self, MainWindow):
        with open(join(RESOURCE_FOLDER, self.theme + ".qss")) as themeFile:
            self.styleSheet = themeFile.read()

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(810, 410)
        MainWindow.setWindowIcon(QIcon(join(RESOURCE_FOLDER, "facercg.png")))
        MainWindow.setMinimumSize(QSize(810, 410))
        MainWindow.setMaximumSize(QSize(810, 410))
        MainWindow.setStyleSheet(self.styleSheet)

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QRect(10, 20, 471, 281))
        font = QFont()
        font.setPointSize(13)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")

        self.formLayoutWidget = QWidget(self.groupBox)
        self.formLayoutWidget.setGeometry(QRect(10, 50, 451, 216))
        font = QFont()
        font.setPointSize(14)
        self.formLayoutWidget.setFont(font)
        self.formLayoutWidget.setObjectName("formLayoutWidget")

        self.formLayout = QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setVerticalSpacing(18)
        self.formLayout.setObjectName("formLayout")

        self.nameLabel = QLabel(self.formLayoutWidget)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.nameLabel.setFont(font)
        self.nameLabel.setObjectName("nameLabel")
        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.nameLabel)

        self.nameLineEdit = QLineEdit(self.formLayoutWidget)
        font = QFont()
        font.setPointSize(14)
        self.nameLineEdit.setFont(font)
        self.nameLineEdit.setText("")
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.nameLineEdit)

        self.studentIdLabel = QLabel(self.formLayoutWidget)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.studentIdLabel.setFont(font)
        self.studentIdLabel.setObjectName("studentIdLabel")
        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.studentIdLabel)

        self.studentIdLineEdit = QLineEdit(self.formLayoutWidget)
        font = QFont()
        font.setPointSize(14)
        self.studentIdLineEdit.setFont(font)
        self.studentIdLineEdit.setObjectName("studentIdLineEdit")
        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.studentIdLineEdit)

        self.birthdayLabel = QLabel(self.formLayoutWidget)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.birthdayLabel.setFont(font)
        self.birthdayLabel.setObjectName("birthdayLabel")
        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.birthdayLabel)

        self.birthdayDateEdit = QDateEdit(self.formLayoutWidget)
        font = QFont()
        font.setPointSize(14)
        self.birthdayDateEdit.setFont(font)
        self.birthdayDateEdit.setObjectName("birthdayDateEdit")
        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.birthdayDateEdit)

        self.classLabel = QLabel(self.formLayoutWidget)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.classLabel.setFont(font)
        self.classLabel.setObjectName("classLabel")
        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.classLabel)

        self.classComboBox = QComboBox(self.formLayoutWidget)
        font = QFont()
        font.setPointSize(14)
        self.classComboBox.setFont(font)
        self.classComboBox.setObjectName("classComboBox")
        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.classComboBox)

        self.imgWidget = ImageWidget(self.centralwidget)
        self.imgWidget.setGeometry(QRect(500, 10, 300, 300))
        self.imgWidget.setMinimumSize(QSize(300, 300))
        self.imgWidget.setMaximumSize(QSize(300, 300))
        self.imgWidget.setAutoFillBackground(False)
        self.imgWidget.setObjectName("imgWidget")

        self.getSampleButton = QPushButton(self.centralwidget)
        self.getSampleButton.setGeometry(QRect(40, 317, 111, 41))
        font = QFont()
        font.setPointSize(12)
        self.getSampleButton.setFont(font)
        self.getSampleButton.setObjectName("getSampleButton")

        self.guideLabel = QLabel(self.centralwidget)
        self.guideLabel.setGeometry(QRect(480, 320, 331, 51))
        font = QFont()
        font.setPointSize(12)
        self.guideLabel.setFont(font)
        self.guideLabel.setAlignment(Qt.AlignCenter)
        self.guideLabel.setObjectName("guideLabel")

        self.saveButton = QPushButton(self.centralwidget)
        self.saveButton.setGeometry(QRect(180, 317, 111, 41))
        font = QFont()
        font.setPointSize(12)
        self.saveButton.setFont(font)
        self.saveButton.setObjectName("saveButton")

        self.cancelButton = QPushButton(self.centralwidget)
        self.cancelButton.setGeometry(QRect(320, 317, 111, 41))
        font = QFont()
        font.setPointSize(12)
        self.cancelButton.setFont(font)
        self.cancelButton.setObjectName("cancelButton")
    
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setGeometry(QRect(0, 0, 810, 26))
        self.menubar.setObjectName("menubar")
        self.fileMenu = QMenu(self.menubar)
        self.fileMenu.setObjectName("fileMenu")
        MainWindow.setMenuBar(self.menubar)
        self.registeredStudentAction = QAction(MainWindow)
        self.registeredStudentAction.setObjectName("registeredStudentAction")
        self.fileMenu.addAction(self.registeredStudentAction)
        self.menubar.addAction(self.fileMenu.menuAction())

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "????ng k?? khu??n m???t h???c sinh"))
        self.groupBox.setTitle(_translate("MainWindow", "Th??ng tin h???c sinh"))
        self.nameLabel.setText(_translate("MainWindow", "H??? v?? T??n"))
        self.studentIdLabel.setText(_translate("MainWindow", "M?? h???c sinh"))
        self.birthdayLabel.setText(_translate("MainWindow", "Ng??y sinh"))
        self.classLabel.setText(_translate("MainWindow", "L???p h???c"))
        self.getSampleButton.setText(_translate("MainWindow", "L???y m???u"))
        self.guideLabel.setText(_translate("MainWindow", "????a m???t v??o ch??nh gi???a camera"))
        self.saveButton.setText(_translate("MainWindow", "L??u"))
        self.cancelButton.setText(_translate("MainWindow", "H???y"))
        self.fileMenu.setTitle(_translate("MainWindow", "Ti???n ??ch"))
        self.registeredStudentAction.setText(_translate("MainWindow", "Danh s??ch HS ???? ????ng k??"))


class StudentRegisterMainWindow(QMainWindow, StudentRegisterMainWindowUI):
    def __init__(self) -> None:
        super().__init__(None)
        self.setupUi(self)

        self.guideLabel.setText("Nh???p th??ng tin c???a b???n\nsau ???? ch???n \"L???y m???u\"")

        self.getSampleButton.clicked.connect(self.onClickedStartBtn)
        self.saveButton.clicked.connect(self.onClickedSaveBtn)
        self.cancelButton.clicked.connect(self.onClickedCancelBtn)
        self.registeredStudentAction.triggered.connect(self.onClickedRegisteredStudent)

        self.image_queue = Queue()

        self.classRepository = ClassRepository(DATABASE_FILE_PATH)
        self.studentRepository = StudentRepository(DATABASE_FILE_PATH)

        self.cur_encoding_path = ""
        self.hasStartedCamera = False
        self.hasDoneSerializingEncoding = False
        self.saveButton.setEnabled(False)

        self.playSuccessSound = QSound(join(RESOURCE_FOLDER, "recognize_success.wav"))
        self.playFailSound = QSound(join(RESOURCE_FOLDER, "recognize_fail.wav"))

        self.loadingData()

    def loadingData(self):
        # L???y d??? li???u l???p v?? set d??? li???u cho classComboBox
        self.classEntities = self.classRepository.get_all_classes()

        # Set d??? li???u cho classComboBox
        self.classComboBox.addItems(tuple(entity.name for entity in self.classEntities))

        # Hi???n th??? logo khi webcam ch??a ???????c b???t
        self.imgWidget.setImage(QImage(join(RESOURCE_FOLDER, "facercg.png")))

    def onClickedStartBtn(self):
        print("startBtn clicked")

        studentName = self.nameLineEdit.text()
        studentId = self.studentIdLineEdit.text()

        # Check n???u c?? l???i nh???p th??ng tin
        err = []
        if studentId is None or studentName == "":
            err.append("??? M?? h???c sinh tr???ng")
        elif studentId.isnumeric() == False:
            err.append("??? M?? h???c sinh ch???a ch??? c??i ho???c k?? t??? ?????c bi???t")
        if studentName is None or studentName == "":
            err.append("??? H??? v?? T??n tr???ng")
        elif studentName.replace(" ", "").isalpha() == False:
            err.append("??? H??? v?? T??n ch???a ch??? s??? ho???c k?? t??? ?????c bi???t")
        if self.studentRepository.get_by_student_id(studentId):
            err.append("??? M?? h???c sinh n??y ???? ???????c ????ng k?? t??? tr?????c")
        
        # N???u c?? l???i th?? hi???n c???a s??? c???nh b??o
        if err:
            msg = QMessageBox()
            msg.setStyleSheet(self.styleSheet)
            msg.setIcon(QMessageBox.Critical)
            msg.setText("\n".join(err))
            msg.setWindowTitle("C?? l???i x???y ra")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return

        # Khi camera ch??a kh???i ?????ng xong th?? hi???n d??ng ch??? n??y
        if self.hasStartedCamera == False:
            self.guideLabel.setText("Vui l??ng ch???...\nCamera ??ang kh???i ?????ng...")

        # T???o lu???ng: webcam v?? ????ng k?? khu??n m???t
        self.webcamHandler = WebcamHandler()
        self.webcamHandler.imgSignal.connect(self.captureImageCallback)
        
        self.registerFace = RegisterFace(self.image_queue, studentId)
        self.registerFace.registerSignal.connect(self.registerCallback)

        # Ch???y lu???ng
        self.webcamHandler.start()
        self.registerFace.start()

        # C???p nh???t tr???ng th??i n??t b???m
        self.getSampleButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.cancelButton.setEnabled(True)

    @pyqtSlot(ndarray)
    def captureImageCallback(self, image):
        self.hasStartedCamera = True

        # Khi ch??a ho??n th??nh encode khu??n m???t th?? v???n hi???n th??? h?????ng d???n
        if self.hasDoneSerializingEncoding == False:
            self.guideLabel.setText("Di chuy???n ?????u khu??n m???t\nTi???n ?????: {}/{}"
                                    .format(self.registerFace.registerProgress, NUM_ENCODE_IMG))

        # push to queue
        self.image_queue.put(image)

        # display image to UI
        self.display_image(image, self.imgWidget) 

    @pyqtSlot(str)
    def registerCallback(self, encode_file_path):
        self.hasDoneSerializingEncoding = True
        if encode_file_path != "":
            self.playSuccessSound.play()
            self.guideLabel.setStyleSheet("color: green")
            self.guideLabel.setText("L???y m???u th??nh c??ng. Vui l??ng ki???m\ntra l???i th??ng tin, sau ???? ch???n \"L??u\"")
            self.cur_encoding_path = encode_file_path
            self.saveButton.setEnabled(True)
            self.getSampleButton.setEnabled(False)
        else:
            self.playFailSound.play()
            self.guideLabel.setStyleSheet("color: red")
            self.guideLabel.setText("L???y m???u th???t b???i\nVui l??ng th??? l???i")
            self.cur_encoding_path = ""
            self.saveButton.setEnabled(False)
            self.getSampleButton.setEnabled(True)

        # Stop camera
        self.webcamHandler.stop()

    # H??m hi???n th??? webcam tr??n giao di???n ch????ng tr??nh
    def display_image(self, img, display):
        h, w, ch = img.shape
        bytes_per_line = ch * w
        qimg = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)
        display.setImage(qimg)    

    # H??m th???c hi???n khi k??ch chu???t n??t "L??u"
    def onClickedSaveBtn(self):
        print("saveBtn clicked")
        if self.cur_encoding_path == "":
            return

        # L??u v??o database   
        studentId = self.studentIdLineEdit.text()
        studentName = self.nameLineEdit.text().title()
        birthday = self.birthdayDateEdit.text()
        className = self.classComboBox.currentText()
        classId = self.getClassIdFromName(className)

        # C???p nh???t th??ng tin h???c sinh
        file_path = join(ENCODING_FOLDER_PATH, studentId + ".pkl")
        if exists(file_path):
            remove(file_path)
        rename(self.cur_encoding_path, file_path)
        self.studentRepository.add_student(StudentEntity(None, studentName, studentId, birthday, classId, file_path))
        self.cur_encoding_path = ""
        self.playSuccessSound.play()
        self.guideLabel.setText("????ng k?? th??nh c??ng!")
        self.saveButton.setEnabled(False)
        self.cancelButton.setText("Tho??t")
        self.cancelButton.setEnabled(True)

    # H??m th???c hi???n khi k??ch chu???t n??t "Hu???"
    def onClickedCancelBtn(self):
        print("cancelBtn clicked")
        try:
            self.webcamHandler.stop()
            self.registerFace.stop()
            if self.cur_encoding_path != "" and exists(self.cur_encoding_path):
                remove(self.cur_encoding_path)
                self.cur_encoding_path = ""
        except AttributeError:
            pass
        
        # K???t th??c ch????ng tr??nh
        raise SystemExit(0)

    # Tr??? v??? l???p h???c c???a h???c sinh
    def getClassIdFromName(self, name) -> int:
        for entity in self.classEntities:
            if entity.name == name:
                return entity.id
        return -1

    # H??m th???c hi???n khi ch???n xem danh s??ch h???c sinh ???? ????ng k??
    def onClickedRegisteredStudent(self):
        registerStudentList = RegisteredStudentListDialog()
        registerStudentList.exec()


if __name__ == "__main__":
    app = QApplication(argv)
    mainWindow = StudentRegisterMainWindow()
    mainWindow.show()
    exit(app.exec_())