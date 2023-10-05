from json import load
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QIcon
from cv2 import line, ellipse
from sqlite3 import connect

bbox_color = {
    "yellow": (77, 209, 255),
    "red": (87, 52, 213),
    "green": (87, 152, 140)
}
langs = {
    "en": 0,
    "vi": 1
}


class UI():
    def __init__(self):
        # Load all configurations from JSON file
        with open(f"./resources/configurations.json") as configurations:
            self.configurations = load(configurations)
            self.register_frames_limit = self.configurations["register_frames_limit"]
        self.get_translations()

    def get_translations(self):
        conn = connect("./resources/translations.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM translations")
        self.transdict = {x[0]: x for x in cursor.fetchall()}
        self.trans = lambda x: self.transdict[x][langs[self.configurations["lang"]]]
        conn.close()

    def show_error_msgbox(self, info):
        msgbox = QMessageBox()
        msgbox.setWindowIcon(QIcon(f"./resources/facercg.png"))
        msgbox.setIcon(QMessageBox.Icon.Critical)
        msgbox.setWindowTitle(self.trans("Errors occured"))
        msgbox.setStandardButtons(QMessageBox.StandardButton.Ok)
        msgbox.setText(info)
        return msgbox.exec()

    def show_yn_msgbox(self, info):
        msgbox = QMessageBox()
        msgbox.setWindowIcon(QIcon(f"./resources/facercg.png"))
        msgbox.setIcon(QMessageBox.Icon.Question)
        msgbox.setWindowTitle(self.trans("Confirm your information"))
        msgbox.setStandardButtons(QMessageBox.StandardButton.Yes |
                                  QMessageBox.StandardButton.No)
        msgbox.setDefaultButton(QMessageBox.StandardButton.No)
        msgbox.setText(info)
        return msgbox.exec()
    
    def show_ok_msgbox(self, info):
        msgbox = QMessageBox()
        msgbox.setWindowIcon(QIcon(f"./resources/facercg.png"))
        msgbox.setIcon(QMessageBox.Icon.Information)
        msgbox.setWindowTitle(self.trans("Confirm"))
        msgbox.setStandardButtons(QMessageBox.StandardButton.Ok)
        msgbox.setText(info)
        msgbox.exec()

    def rounded_rect(self, img, pt1, pt2, color, thickness=2, r=3, d=15):
        color = bbox_color[color]
        x1, y1 = pt1
        x2, y2 = pt2
        line(img, (x1 + r, y1), (x1 + r + d, y1), color, thickness)
        line(img, (x1, y1 + r), (x1, y1 + r + d), color, thickness)
        ellipse(img, (x1 + r, y1 + r), (r, r), 180, 0, 90, color, thickness)
        line(img, (x2 - r, y1), (x2 - r - d, y1), color, thickness)
        line(img, (x2, y1 + r), (x2, y1 + r + d), color, thickness)
        ellipse(img, (x2 - r, y1 + r), (r, r), 270, 0, 90, color, thickness)
        line(img, (x1 + r, y2), (x1 + r + d, y2), color, thickness)
        line(img, (x1, y2 - r), (x1, y2 - r - d), color, thickness)
        ellipse(img, (x1 + r, y2 - r), (r, r), 90, 0, 90, color, thickness)
        line(img, (x2 - r, y2), (x2 - r - d, y2), color, thickness)
        line(img, (x2, y2 - r), (x2, y2 - r - d), color, thickness)
        ellipse(img, (x2 - r, y2 - r), (r, r), 0, 0, 90, color, thickness)
