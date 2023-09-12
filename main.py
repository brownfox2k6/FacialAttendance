from sys import argv

from PyQt6.QtWidgets import QMainWindow, QPushButton, QLabel, QApplication
from PyQt6.QtGui import QIcon, QImage, QPixmap
from PyQt6.QtCore import Qt, QMetaObject

from recognize_ui import RecognizeWindow
from register_ui import RegisterWindow
from init import UI


class MainWindow(QMainWindow, UI):
    def __init__(self):
        super().__init__()

        self.setObjectName("mainWindow")
        self.setWindowIcon(QIcon(f"./resources/facercg.png"))
        self.setWindowTitle(self.trans("Facial attendance system"))
        self.setMinimumSize(500, 300)
        self.setMaximumSize(500, 300)

        self.title_label = QLabel(self)
        self.title_label.setGeometry(10, 0, 365, 120)
        self.title_label.setText(self.trans("Facial attendance\nsystem"))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            font-family: 'Segoe UI Semibold';
            font-size: 24pt;
        """)

        self.logo_image = QLabel(self)
        self.logo_image.setGeometry(365, 10, 100, 100)
        self.logo_image.setPixmap(QPixmap.fromImage(QImage(f"./resources/facercg.png")))

        self.enter_register_button = QPushButton(self)
        self.enter_register_button.setGeometry(35, 120, 200, 70)
        self.enter_register_button.setText(self.trans("Face registration"))
        self.enter_register_button.clicked.connect(self.enter_register)

        self.enter_recognize_button = QPushButton(self)
        self.enter_recognize_button.setGeometry(35, 210, 200, 70)
        self.enter_recognize_button.setText(self.trans("Attendance check"))
        self.enter_recognize_button.clicked.connect(self.enter_recognize)

        self.enter_utilities_button = QPushButton(self)
        self.enter_utilities_button.setGeometry(270, 120, 200, 70)
        self.enter_utilities_button.setText(self.trans("Utilities"))
        self.enter_utilities_button.clicked.connect(self.enter_utilities)

        self.enter_settings_button = QPushButton(self)
        self.enter_settings_button.setGeometry(270, 210, 200, 70)
        self.enter_settings_button.setText(self.trans("Settings"))
        self.enter_settings_button.clicked.connect(self.enter_settings)

        self.registerWindow = None
        self.recognizeWindow = None
        self.utilitiesWindow = None
        self.settingsWindow = None

        QMetaObject.connectSlotsByName(self)

    def enter_register(self):
        if not any((self.registerWindow, self.recognizeWindow,
                    self.utilitiesWindow, self.settingsWindow)):
            self.registerWindow = RegisterWindow()
            self.registerWindow.show()

    def enter_recognize(self):
        if not any((self.registerWindow, self.recognizeWindow,
                    self.utilitiesWindow, self.settingsWindow)):
            self.recognizeWindow = RecognizeWindow()
            self.recognizeWindow.show()

    def enter_utilities(self):
        pass

    def enter_settings(self):
        pass


if __name__ == "__main__":
    app = QApplication(argv)
    window = MainWindow()
    window.show()
    app.exec()