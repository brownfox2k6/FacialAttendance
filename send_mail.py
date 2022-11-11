from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from msvcrt import getch
from os.path import join
from pickle import dumps, loads
from smtplib import SMTP, SMTPAuthenticationError
from ssl import create_default_context
from time import sleep, strptime

from colorama import init as clinit
from cryptography.fernet import Fernet
from email_validator import EmailNotValidError, validate_email
from pandas import DataFrame

from constants import DATABASE_FILE_PATH, RESOURCE_FOLDER, SMTP_INSTRUCTION
from db_access.attendance_repository import AttendanceRepository
from db_access.class_repository import ClassRepository

clinit(wrap=True)
TODAY = date.today().strftime("%d/%m/%Y")
studentIDs, studentNames, birthdays, classNames, enterTimes, statuses = 0, 1, 2, 3, 4, 5


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# source: https://pypi.org/project/pretty-html-table/
def build_table(
        df,
        change_color = False,
        font_size='medium', 
        font_family='Arial', 
        text_align='left', 
        width='auto', 
        index=False, 
        odd_bg_color=None,
        border_bottom_color=None,
        escape=True,
        padding="5px 20px 5px 5px",
        float_format=None):

    # Set color
    color, border_bottom, odd_background_color, header_background_color = '#FFFFFF', '2px solid #305496', '#D9E1F2', '#305496'

    if odd_bg_color:
        odd_background_color = odd_bg_color

    if border_bottom_color:
        border_bottom = border_bottom_color 

    df_html_output = df.iloc[[0]].to_html(
        na_rep="", 
        index=index, 
        border=0, 
        escape=escape, 
        float_format=float_format,
    )
    # change format of header
    if index:
        df_html_output = df_html_output.replace('<th>'
                                                ,'<th style = "background-color: ' + header_background_color
                                                + ';font-family: ' + font_family
                                                + ';font-size: ' + str(font_size)
                                                + ';color: ' + color
                                                + ';text-align: ' + text_align
                                                + ';border-bottom: ' + border_bottom
                                                + ';padding: ' + padding
                                                + ';width: ' + str(width) + '">', len(df.columns)+1)

        df_html_output = df_html_output.replace('<th>'
                                                ,'<th style = "background-color: ' + odd_background_color
                                                + ';font-family: ' + font_family
                                                + ';font-size: ' + str(font_size)
                                                + ';text-align: ' + text_align
                                                + ';padding: ' + padding
                                                + ';width: ' + str(width) + '">')

    else:
        df_html_output = df_html_output.replace('<th>'
                                                ,'<th style = "background-color: ' + header_background_color
                                                + ';font-family: ' + font_family
                                                + ';font-size: ' + str(font_size)
                                                + ';color: ' + color
                                                + ';text-align: ' + text_align
                                                + ';border-bottom: ' + border_bottom
                                                + ';padding: ' + padding
                                                + ';width: ' + str(width) + '">')

    #change format of table
    df_html_output = df_html_output.replace('<td>'
                                            ,'<td style = "background-color: ' + odd_background_color
                                            + ';font-family: ' + font_family
                                            + ';font-size: ' + str(font_size)
                                            + ';text-align: ' + text_align
                                            + ';padding: ' + padding
                                            + ';width: ' + str(width) + '">')
    body = """<p>""" + format(df_html_output)

    a = 1
    while a != len(df):
        df_html_output = df.iloc[[a]].to_html(na_rep = "", index = index, header = False, escape=escape)
            
        # change format of index
        df_html_output = df_html_output.replace('<th>'
                                                ,'<th style = "background-color: ' + odd_background_color
                                                + ';font-family: ' + font_family
                                                + ';font-size: ' + str(font_size)
                                                + ';text-align: ' + text_align
                                                + ';padding: ' + padding
                                                + ';width: ' + str(width) + '">')

        #change format of table
        df_html_output = df_html_output.replace('<td>'
                                                ,'<td style = "background-color: ' + odd_background_color
                                                + ';font-family: ' + font_family
                                                + ';font-size: ' + str(font_size)
                                                + ';text-align: ' + text_align
                                                + ';padding: ' + padding
                                                + ';width: ' + str(width) + '">')

        body = body + format(df_html_output)
        a += 1

    body = body + """</p>"""

    body = body.replace("""</td>
    </tr>
  </tbody>
</table>
            <table border="1" class="dataframe">
  <tbody>
    <tr>""","""</td>
    </tr>
    <tr>""").replace("""</td>
    </tr>
  </tbody>
</table><table border="1" class="dataframe">
  <tbody>
    <tr>""","""</td>
    </tr>
    <tr>""")


    # Change color for detailed attendance table
    if change_color:
        body = body.replace(r"\n'", "").split("<tr>")
        body_res = []
        for item in body:
            if "Vắng" in item:
                body_res.append(item.replace("#D9E1F2", "#FAA0A0"))
            elif "Đúng giờ" in item:
                body_res.append(item.replace("#D9E1F2", "#DAF7A6"))
            elif "Muộn" in item:
                body_res.append(item.replace("#D9E1F2", "#FFE4B5"))
            else:
                body_res.append(item)
        return "<tr>".join(body_res)
    
    return body.replace(r"\n'", "")


def get_class_attendance_info(className, day) -> tuple[list, list, list, list, list, list]:
    studentIDs, studentNames, birthdays, classNames, enterTimes, statuses = [], [], [], [], [], []

    for row in AttendanceRepository(DATABASE_FILE_PATH).get_student_enter_time(className, day):
        studentID, studentName, birthday, startTime, enterTime = row[:5]

        if enterTime is None:
            enterTimes.append("")
            status = "Vắng"
        else:
            enterTimes.append(enterTime[11:])
            status = "Đúng giờ" if strptime(enterTime, "%d/%m/%Y %H:%M:%S") <=\
                        strptime(day + " " + startTime, "%d/%m/%Y %H:%M:%S") else "Muộn"

        studentIDs.append(studentID)
        studentNames.append(studentName)
        birthdays.append(birthday)
        classNames.append(className)
        statuses.append(status)

    return studentIDs, studentNames, birthdays, classNames, enterTimes, statuses


def readKeyFile() -> tuple[str, str]:
    with open(join(RESOURCE_FOLDER, "key.bin"), "rb") as keyFile:
        fernet = Fernet(loads(bytes(keyFile.readline())))
        user = loads(bytes(keyFile.readline()))
        password = loads(bytes(keyFile.readline()))

    # return decoded user, decoded password
    return fernet.decrypt(user).decode(), fernet.decrypt(password).decode()


def writeKeyFile(user, password) -> None:
    key = Fernet.generate_key()
    fernet = Fernet(key)

    with open(join(RESOURCE_FOLDER, "key.bin"), "wb") as keyFile:
        keyFile.write(dumps(key))
        keyFile.write("\n".encode("utf-8"))
        keyFile.write(dumps(fernet.encrypt(user.encode("utf-8"))))
        keyFile.write("\n".encode("utf-8"))
        keyFile.write(dumps(fernet.encrypt(password.encode("utf-8"))))


def UsernameInput() -> str:
    while True:
        try:
            print(f"{bcolors.WARNING}Tên tài khoản Gmail (abc@gmail.com):  {bcolors.ENDC}", end="")
            user = input()
            validate_email(user)
            return user
        except EmailNotValidError as err:
            print(f"{bcolors.FAIL}{err}{bcolors.ENDC}\n")


def PasswordInput(user) -> str:
    while True:
        print(f"{bcolors.BOLD}Nhập 'h' để được hướng dẫn cách lấy mật khẩu SMTP hoặc bỏ trống để nhập lại tên tài khoản Gmail{bcolors.ENDC}")
        print(f"{bcolors.WARNING}Mật khẩu SMTP cho {user}:  {bcolors.ENDC}", end="")
        password = input().lower()
        if password == "" or (len(password) == 16 and password.isalpha()):
            return password
        elif password == "h":
            print(f"{bcolors.OKCYAN}{SMTP_INSTRUCTION}{bcolors.ENDC}")
        else:
            print(f"{bcolors.FAIL}Mật khẩu SMTP là một chuỗi gồm 16 ký tự chữ cái{bcolors.ENDC}\n")


def loginMail(user, password) -> SMTP:
    # Initialize flag variables
    hasDoneUsernameInput, hasDonePasswordInput, saveSignal = (True, True, False) if user else (False, False, True)

    # Lặp cho đến khi nhập được tên tài khoản Gmail và mật khẩu SMTP đúng
    while True:

        # Nhập tên tài khoản Gmail
        if hasDoneUsernameInput == False:
            user = UsernameInput()

        # Nhập mật khẩu SMTP
        # * chỉ có thể bỏ qua đoạn này ở vòng lặp thứ nhất thôi :)
        if hasDonePasswordInput == False:
            saveSignal = True
            password = PasswordInput(user)

            # Nếu password == "" tức người dùng muốn nhập lại tên tài khoản Gmail
            if not password:
                hasDoneUsernameInput = False
                continue

        # Nhập mật khẩu đúng yêu cầu rồi thì đặt flag để lỡ có đăng nhập lỗi
        # thì thực hiện đăng nhập lại mà không phải nhập lại tên tài khoản
        hasDoneUsernameInput = True

        # Đăng nhập cho đến khi thành công
        while True:
            try:
                server = SMTP(host="smtp.gmail.com", port=587)
                server.ehlo()   # Can be omitted
                server.starttls(context=create_default_context())   # Secure the connection
                server.ehlo()   # Can be omitted
                server.login(user, password)
                print(f"{bcolors.OKCYAN}Đăng nhập thành công {bcolors.ENDC}", end="")
                print(f"{bcolors.WARNING}{user}{bcolors.ENDC}\n")
                if saveSignal:
                    writeKeyFile(user, password)
                    print(f"{bcolors.OKGREEN}Lưu tài khoản thành công.{bcolors.ENDC}")
                return server

            # Gặp lỗi này thì cho đăng nhập lại
            except SMTPAuthenticationError:
                print(f"{bcolors.FAIL}Tên tài khoản Gmail hoặc Mật khẩu SMTP sai{bcolors.ENDC}\n")
                hasDonePasswordInput = False
                break

            # Còn các lỗi khác thì dừng chương trình một lúc rồi thử lại
            except Exception as err:
                print(f"{bcolors.FAIL}{err}{bcolors.ENDC}")
                sleep(2)


def sendMail() -> None:
    try:
        user, password = readKeyFile()
    except FileNotFoundError:
        user, password = "", ""

    server = loginMail(user, password)

    for item in ClassRepository(DATABASE_FILE_PATH).get_all_classes():
        attendanceInfos = get_class_attendance_info(item.name, TODAY)
        recipient = item.mail_recipient
        name = item.name

        if attendanceInfos[studentIDs] != [None]:
            if recipient != None:
                _statuses = attendanceInfos[statuses]

                # Initialize message
                message = MIMEMultipart()
                message["Subject"] = "THÔNG TIN ĐIỂM DANH HỌC SINH LỚP {} NGÀY {}".format(name, TODAY)
                message["From"] = user
                message["To"] = recipient

                # Attach summary table
                summary = {
                    "Đúng giờ": [_statuses.count("Đúng giờ")],
                    "Muộn": [_statuses.count("Muộn")],
                    "Vắng": [_statuses.count("Vắng")]
                }
                summary = build_table(DataFrame(summary))
                message.attach(MIMEText(summary, "html"))

                # Attach detailed attendance table
                body = {
                    "STT": list(range(1, len(_statuses)+1)),
                    "Tên học sinh": attendanceInfos[studentNames],
                    "Mã học sinh": attendanceInfos[studentIDs],
                    "Ngày sinh": attendanceInfos[birthdays],
                    "Thời gian điểm danh": attendanceInfos[enterTimes],
                    "Trạng thái": _statuses
                }
                body = build_table(DataFrame(body), change_color=True)
                message.attach(MIMEText(body, "html"))

                # Send mail
                server.sendmail(user, recipient, message.as_string())
                print("{}{:6s} - Đã gửi{}".format(bcolors.OKGREEN, name, bcolors.ENDC))

            else:
                print("{}{:6s} - Không tìm thấy địa chỉ Gmail của giáo viên trong database{}".format(
                    bcolors.FAIL, name, bcolors.ENDC))

        else:
            print("{}{:6s} - Không có học sinh đã đăng ký trong hệ thống{}".format(bcolors.FAIL, name, bcolors.ENDC))

    server.quit()
    print(f"\n{bcolors.OKGREEN}Gửi thông tin điểm danh thành công{bcolors.ENDC}")
    print(f"{bcolors.OKCYAN}Ấn phím bất kỳ để thoát{bcolors.ENDC}")
    getch()


sendMail()
