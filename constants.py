NUM_ENCODE_IMG            = 5
NUM_RECOGNIZE_IMG         = 10

RECOGNIZE_FACES_TOLERANCE = 0.3
REGISTER_FACES_TOLERANCE  = 0.2

DATABASE_FILE_PATH        = ".\\database\\attendance.db"
ENCODING_FOLDER_PATH      = ".\\database\\encoding_data"
ENCODING_FILE_EXT         = ".pkl"
FACE_LOCATIONS_MODEL      = "hog"
RESOURCE_FOLDER           = ".\\resources"
ENCODING_DATA             = "encodings"
ENCODING_NAME             = "names"

SMTP_INSTRUCTION = """
Đầu tiên, bạn cần truy cập https://myaccount.google.com/ sau đó đăng nhập tài khoản Gmail của bạn
Sau đó, vào mục Bảo mật (Security) và bật Xác minh 2 bước (2-Step Verification) nếu trạng thái này đang tắt
Tiếp theo, chọn Mật khẩu ứng dụng (App passwords)
Trong phần Chọn ứng dụng (Select app), bạn chọn Khác (Other) và đặt tên tuỳ ý (nên đặt là SMTP cho tiện)
Cuối cùng, ấn chọn TẠO (GENERATE), mật khẩu SMTP sẽ được hiện lên trên màn hình, bạn hãy copy mật khẩu đó và dán vào đây
"""