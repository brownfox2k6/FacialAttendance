from cv2 import (CAP_DSHOW, CAP_PROP_BUFFERSIZE, CAP_PROP_FPS,
                 CAP_PROP_FRAME_HEIGHT, CAP_PROP_FRAME_WIDTH, COLOR_BGR2RGB,
                 VideoCapture, cvtColor)
from numpy import ndarray
from PyQt5.QtCore import QThread, pyqtSignal


class WebcamHandler(QThread):
    imgSignal = pyqtSignal(ndarray)

    def __init__(self):
        QThread.__init__(self)
        self.capturing = True

    # Tạo một luồng để lấy ảnh từ webcam
    def run(self):

        # Mở webcam, 0 là id của webcam
        cap = VideoCapture(0, CAP_DSHOW)

        cap.set(CAP_PROP_FRAME_WIDTH, 1080)
        cap.set(CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(CAP_PROP_BUFFERSIZE, 3)
        cap.set(CAP_PROP_FPS, 30)

        while self.capturing:
            if cap.grab():
                image = cap.retrieve(0)[1]
                
                # Trả về khung hình webcam
                if image is not None:
                    # Vì hệ thống điểm danh chỉ nhận diện một khuôn mặt một lúc
                    # nên nếu để độ phân giải là 1080x720 là dư thừa
                    # => để độ phân giải 300x300 là tối ưu
                    # vừa không dư thừa vừa giảm khối lượng xử lý của chương trình
                    # convert color from BGR (default) to RGB
                    self.imgSignal.emit(cvtColor(image[210:510, 390:690], COLOR_BGR2RGB))

            else:
                print("Error: can't grab camera image")
                break

        # Sau khi chạy xong, giải phóng tài nguyên dùng cho webcam
        cap.release()

    # Hàm dừng webcam
    def stop(self):
        self.capturing = False
        self.wait()
