from json import load

from cv2 import (CAP_DSHOW, CAP_PROP_FRAME_HEIGHT,
                 CAP_PROP_FRAME_WIDTH, VideoCapture)
from numpy import ndarray
from PyQt6.QtCore import QThread, pyqtSignal


class WebcamThread(QThread):
    frame_to_display_signal = pyqtSignal(ndarray)
    frame_to_process_signal = pyqtSignal(ndarray)

    def __init__(self):
        super().__init__()
        self.load_configurations()
        self.init_webcam(300, 300)
        self.counter = 0

    def load_configurations(self):
        with open(f"./resources/configurations.json") as configurations:
            data = load(configurations)
            self.webcam_number = data["webcam"]
            self.face_process_frequency = data["face_process_frequency"]
            del data

    def init_webcam(self, out_w, out_h):
        self.cap = VideoCapture(self.webcam_number, CAP_DSHOW)
        self.tl_x = int(self.cap.get(CAP_PROP_FRAME_WIDTH) - out_w) >> 1
        self.tl_y = int(self.cap.get(CAP_PROP_FRAME_HEIGHT) - out_h) >> 1
        self.br_x = self.tl_x + out_w
        self.br_y = self.tl_y + out_h

    def inc_counter(self):
        self.counter += 1
        if self.counter == self.face_process_frequency:
            self.counter = 0

    def get_frame(self):
        orig_frame = self.cap.read()[1]
        cropped_frame = orig_frame[self.tl_y:self.br_y,
                                   self.tl_x:self.br_x]
        return cropped_frame

    def run(self):
        while self.isRunning():
            frame = self.get_frame()
            if self.counter == 0:
                self.frame_to_process_signal.emit(frame)
            self.frame_to_display_signal.emit(frame)
            self.inc_counter()
