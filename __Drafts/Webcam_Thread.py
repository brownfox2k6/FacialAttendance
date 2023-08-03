import json

import cv2
import numpy
from PyQt6 import QtCore

import constants


class WebcamThread(QtCore.QThread):
    frame_signal = QtCore.pyqtSignal(numpy.ndarray)

    def __init__(self):
        super().__init__()
        with open(f"{constants.RESOURCE_FOLDER}/configurations.json") as configurations:
            self.webcam_number = json.load(configurations)["webcam_number"]

    def run(self):
        cap = cv2.VideoCapture(self.webcam_number, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, constants.W)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, constants.H)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, constants.BUFFERSIZE)
        while self.isRunning():
            ret, frame = cap.read()
            if ret:
                self.frame_signal.emit(frame[210:510, 390:690])
        cap.release()
