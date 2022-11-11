from os.path import join
from pickle import dumps

from face_recognition import compare_faces, face_encodings, face_locations

from constants import (REGISTER_FACES_TOLERANCE, ENCODING_DATA,
                       ENCODING_FOLDER_PATH, ENCODING_NAME,
                       FACE_LOCATIONS_MODEL, NUM_ENCODE_IMG)
from PyQt5.QtCore import QThread, pyqtSignal


class RegisterFace(QThread):
    registerSignal = pyqtSignal(str)

    def __init__(self, image_queue, label) -> None:
        QThread.__init__(self)
        self.label = label
        self.image_queue = image_queue
        self.encoding = True
        self.registerProgress = 0

    def run(self):
        knownEncodings, knownNames = [], []

        while self.registerProgress < NUM_ENCODE_IMG and self.encoding:
            if self.image_queue.qsize() > 0:
                # Lấy ảnh từ queue
                image = self.image_queue.get()

                # Tìm những khuôn mặt có trong khung hình
                faces = face_locations(image, model=FACE_LOCATIONS_MODEL)

                # Chỉ chấp nhận một khuôn mặt trong khung hình
                if len(faces) == 1:

                    # Vì chỉ có một khung hình nên len(encoding) = 1, lấy ra giá trị duy nhất
                    encoding = face_encodings(image, faces)[0]

                    # Nếu ảnh hiện tại không khớp với bất kì ảnh nào trước đó thì chấp nhận
                    if True not in compare_faces(knownEncodings, encoding, tolerance=REGISTER_FACES_TOLERANCE):
                        knownEncodings.append(encoding)
                        knownNames.append(self.label)
                        self.registerProgress += 1

        # Ghi dữ liệu encodings + names ra file
        file_path = join(ENCODING_FOLDER_PATH, self.label + ".tmp")
        with open(file_path, "wb") as temporaryEncodeFile:
            temporaryEncodeFile.write(dumps({ENCODING_DATA:tuple(knownEncodings), ENCODING_NAME:tuple(knownNames)}))

        self.registerSignal.emit(file_path)

    # Hàm kết thúc chương trình
    def stop(self):
        self.encoding = False

