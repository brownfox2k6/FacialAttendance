# For testing purpose only

from cv2 import FaceDetectorYN, FaceRecognizerSF, imread
import os, pickle

src = input("Enter path of source folder: ")
dst = input("Enter path of destination folder: ")
dnn_models = input("Enter path of the folder contais models: ")

recognizer = FaceRecognizerSF.create(
    model = f"{dnn_models}/face_recognition_sface_2021dec.onnx",
    config = ""
)

for person in os.listdir(src):
    db = []
    for f in os.listdir(f'{src}/{person}'):
        img = imread(f'{src}/{person}/{f}')
        h, w, ch = img.shape
        detector = FaceDetectorYN.create(
            model = f"{dnn_models}/face_detection_yunet_2023mar.onnx",
            config = "",
            input_size = (w, h),
            score_threshold = 0.7,
            nms_threshold = 0.3,
            top_k = 5000
        )
        face = detector.detect(img)[1]
        if face is None or len(face) != 1:
            print("Failed")
            exit()
        face = face[0]
        face_align = recognizer.alignCrop(img, face)
        face_feature = recognizer.feature(face_align)
        db.append(face_feature)
    with open(f'{dst}/{person}.pkl', "wb") as f:
        pickle.dump(db, f)
