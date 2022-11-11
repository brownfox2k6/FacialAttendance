from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget


class ImageWidget(QWidget):
    def __init__(self, parent=None):
        super(ImageWidget, self).__init__(parent)
        self.image = None

    def setImage(self, image):
        scale_img = image.scaled(self.width(), self.height(),
            Qt.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self.image = scale_img
        self.update()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        if self.image:
            qp.drawImage(QPoint(0, 0), self.image)
        qp.end()
