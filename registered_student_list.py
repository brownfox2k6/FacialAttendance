from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog

from constants import DATABASE_FILE_PATH
from db_access.class_repository import ClassRepository
from db_access.student_repository import StudentRepository
from table_model import TableModel
from os.path import join
from constants import RESOURCE_FOLDER


class RegisteredStudentListUI(object):
    def __init__(self) -> None:
        with open(join(RESOURCE_FOLDER, "theme.txt")) as specifiedTheme:
            self.theme = "light" if specifiedTheme.read() == "1" else "dark"

    def setupUi(self, Dialog):
        with open(join(RESOURCE_FOLDER, self.theme + ".qss")) as themeFile:
            self.styleSheet = themeFile.read()

        Dialog.setObjectName("Dialog")
        Dialog.resize(754, 488)
        Dialog.setStyleSheet(self.styleSheet)
        Dialog.setMinimumSize(QtCore.QSize(754, 488))
        Dialog.setMaximumSize(QtCore.QSize(754, 488))

        self.classComboBox = QtWidgets.QComboBox(Dialog)
        self.classComboBox.setGeometry(QtCore.QRect(101, 20, 100, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.classComboBox.setFont(font)
        self.classComboBox.setObjectName("comboBox")

        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(20, 20, 55, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setObjectName("label")

        self.studentTableView = QtWidgets.QTableView(Dialog)
        self.studentTableView.setGeometry(QtCore.QRect(20, 70, 711, 391))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.studentTableView.setFont(font)
        self.studentTableView.setObjectName("tableView")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Danh sách học sinh đã đăng ký"))
        self.label.setText(_translate("Dialog", "Lớp"))


class RegisteredStudentListDialog(QDialog, RegisteredStudentListUI):
    def __init__(self) -> None:
        super().__init__(None)
        self.setupUi(self)
        # set data for table
        self.studentTableHeader = ["Họ và tên", "Mã học sinh", "Ngày sinh", "Lớp"]
        self.classComboBox.currentIndexChanged.connect(self.onSelectedClassChanged)
        self.studentRepository = StudentRepository(DATABASE_FILE_PATH)
        self.classRepository = ClassRepository(DATABASE_FILE_PATH)
        self.loadingData()

    def loadingData(self):
        # Get data of class
        self.classEntities = self.classRepository.get_all_classes()
        classNames = ["Tất cả"]
        for entity in self.classEntities:
            classNames.append(entity.name)

        # Set data for combobox class
        self.classComboBox.addItems(classNames) 
        self.classComboBox.setCurrentIndex(0)                

    def onSelectedClassChanged(self):
        className = self.classComboBox.currentText()
        classId = self.getClassIdFromName(className)

        self.model = self.studentRepository.get_students_by_class_id(classId)
        self.registeredStudentModel = TableModel(self.model, self.studentTableHeader)
        self.studentTableView.setModel(self.registeredStudentModel)

        self.studentTableView.setColumnWidth(0, 210)
        self.studentTableView.setColumnWidth(1, 160)
        self.studentTableView.setColumnWidth(2, 176)
        self.studentTableView.setColumnWidth(3, 114)

    def getClassIdFromName(self, name) -> int:
        for entity in self.classEntities:
            if entity.name == name:
                return entity.id
        return -1
