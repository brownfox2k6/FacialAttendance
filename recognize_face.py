from os import listdir
from os.path import join
from pickle import loads
from numpy import amin, where

from face_recognition import face_distance, face_encodings, face_locations

from constants import (ENCODING_DATA, ENCODING_FILE_EXT, ENCODING_FOLDER_PATH,
                       ENCODING_NAME, FACE_LOCATIONS_MODEL, NUM_RECOGNIZE_IMG,
                       RECOGNIZE_FACES_TOLERANCE)
from PyQt5.QtCore import QThread, pyqtSignal

# Hàm nhận diện
def recognize(encoding_data, image) -> str:

    # Tìm toạ độ của các khuôn mặt trong khung hình
    faceLocations = face_locations(image, model=FACE_LOCATIONS_MODEL)
    faces = len(faceLocations)

    # Nếu không tìm thấy khuôn mặt trong khung hình
    if faces == 0:
        return "NoFace"

    # Nếu xuất hiện nhiều hơn một khuôn mặt trong khung hình
    elif faces > 1:
        return "MoreThanOneFace"

    # So sánh với các khuôn mặt trong database và tìm khoảng cách nhỏ nhất minDistance
    faceDistances = face_distance(encoding_data[ENCODING_DATA], face_encodings(image, faceLocations)[0])
    minDistance = amin(faceDistances)

    # Nếu minDistance thoả mãn điều kiện tolerance
    # thì tìm index của minDistance và trả về tên học sinh:
    if minDistance <= RECOGNIZE_FACES_TOLERANCE:
        minIndexes = where(faceDistances == minDistance)[0]
        if len(minIndexes) == 1:
            return encoding_data[ENCODING_NAME][minIndexes[0]]

    # Còn không thì trả về tên "Unknown"
    return "Unknown"


class RecognizeFace(QThread):
    recognizedSignal = pyqtSignal(str, str)

    def __init__(self, image_queue) -> None:
        QThread.__init__(self)
        self.image_queue = image_queue
        self.running = True
        self.loading_finished = False
        self.loading_data()
        self.attemptCount = -1

    # Hàm tiền xử lý (lấy dữ liệu)
    def loading_data(self):
        encodings, names = [], []

        # Tải dữ liệu encoding
        for file in listdir(ENCODING_FOLDER_PATH):
            if file.endswith(ENCODING_FILE_EXT):
                with open(join(ENCODING_FOLDER_PATH, file), "rb") as encodeFile:
                    fileData = loads(bytes(encodeFile.read()))

                encodings.extend(fileData[ENCODING_DATA])
                names.extend(fileData[ENCODING_NAME])

        # Chuyển sang tuple -> tối ưu thời gian chạy
        self.encoding_data = {ENCODING_DATA:tuple(encodings), ENCODING_NAME:tuple(names)}
        self.loading_finished = True

    # Hàm chạy chương trình
    def run(self):
        while self.running:
            if self.image_queue.qsize() > 0:
                self.attemptCount += 1

                # Nhận diện khuôn mặt, trả về tên
                name = recognize(self.encoding_data, self.image_queue.get())
                if name == "NoFace":
                    result = "NoFace"
                elif name == "MoreThanOneFace":
                    result = "MoreThanOneFace"
                elif name == "Unknown":
                    result = "Fail"
                else:
                    result = "Success"

                # Sau một thời gian không nhận diện được khuôn mặt thì không điểm danh nữa
                if result != "Fail" or self.attemptCount == NUM_RECOGNIZE_IMG:
                    self.attemptCount = -1
                    self.recognizedSignal.emit(result, name)

    # Hàm kết thúc chương trình
    def stop(self):
        self.running = False
