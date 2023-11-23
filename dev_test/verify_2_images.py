# For testing purpose only

from cv2 import FaceDetectorYN, FaceRecognizerSF, FaceRecognizerSF_FR_COSINE, imread

dnn_models = input("Enter path of the folder contains models: ")
img1 = input("Enter path of first image: ")
img2 = input("Enter path of second image: ")

recognizer = FaceRecognizerSF.create(
    model = f"{dnn_models}/face_recognition_sface_2021dec.onnx",
    config = ""
)

def get_feature(path):
    img = imread(path)
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
        print("Failed - There is an image which not has exactly one face.")
        exit()
    face = face[0]
    face_align = recognizer.alignCrop(img, face)
    face_feature = recognizer.feature(face_align)
    return face_feature

f1 = get_feature(img1)
f2 = get_feature(img2)
similarity = recognizer.match(f1, f2, FaceRecognizerSF_FR_COSINE)

print("Similarity:", similarity)
