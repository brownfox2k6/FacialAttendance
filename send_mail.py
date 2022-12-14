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
            if "V???ng" in item:
                body_res.append(item.replace("#D9E1F2", "#FAA0A0"))
            elif "????ng gi???" in item:
                body_res.append(item.replace("#D9E1F2", "#DAF7A6"))
            elif "Mu???n" in item:
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
            status = "V???ng"
        else:
            enterTimes.append(enterTime[11:])
            status = "????ng gi???" if strptime(enterTime, "%d/%m/%Y %H:%M:%S") <=\
                        strptime(day + " " + startTime, "%d/%m/%Y %H:%M:%S") else "Mu???n"

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
            print(f"{bcolors.WARNING}T??n t??i kho???n Gmail (abc@gmail.com):  {bcolors.ENDC}", end="")
            user = input()
            validate_email(user)
            return user
        except EmailNotValidError as err:
            print(f"{bcolors.FAIL}{err}{bcolors.ENDC}\n")


def PasswordInput(user) -> str:
    while True:
        print(f"{bcolors.BOLD}Nh???p 'h' ????? ???????c h?????ng d???n c??ch l???y m???t kh???u SMTP ho???c b??? tr???ng ????? nh???p l???i t??n t??i kho???n Gmail{bcolors.ENDC}")
        print(f"{bcolors.WARNING}M???t kh???u SMTP cho {user}:  {bcolors.ENDC}", end="")
        password = input().lower()
        if password == "" or (len(password) == 16 and password.isalpha()):
            return password
        elif password == "h":
            print(f"{bcolors.OKCYAN}{SMTP_INSTRUCTION}{bcolors.ENDC}")
        else:
            print(f"{bcolors.FAIL}M???t kh???u SMTP l?? m???t chu???i g???m 16 k?? t??? ch??? c??i{bcolors.ENDC}\n")


def loginMail(user, password) -> SMTP:
    # Initialize flag variables
    hasDoneUsernameInput, hasDonePasswordInput, saveSignal = (True, True, False) if user else (False, False, True)

    # L???p cho ?????n khi nh???p ???????c t??n t??i kho???n Gmail v?? m???t kh???u SMTP ????ng
    while True:

        # Nh???p t??n t??i kho???n Gmail
        if hasDoneUsernameInput == False:
            user = UsernameInput()

        # Nh???p m???t kh???u SMTP
        # * ch??? c?? th??? b??? qua ??o???n n??y ??? v??ng l???p th??? nh???t th??i :)
        if hasDonePasswordInput == False:
            saveSignal = True
            password = PasswordInput(user)

            # N???u password == "" t???c ng?????i d??ng mu???n nh???p l???i t??n t??i kho???n Gmail
            if not password:
                hasDoneUsernameInput = False
                continue

        # Nh???p m???t kh???u ????ng y??u c???u r???i th?? ?????t flag ????? l??? c?? ????ng nh???p l???i
        # th?? th???c hi???n ????ng nh???p l???i m?? kh??ng ph???i nh???p l???i t??n t??i kho???n
        hasDoneUsernameInput = True

        # ????ng nh???p cho ?????n khi th??nh c??ng
        while True:
            try:
                server = SMTP(host="smtp.gmail.com", port=587)
                server.ehlo()   # Can be omitted
                server.starttls(context=create_default_context())   # Secure the connection
                server.ehlo()   # Can be omitted
                server.login(user, password)
                print(f"{bcolors.OKCYAN}????ng nh???p th??nh c??ng {bcolors.ENDC}", end="")
                print(f"{bcolors.WARNING}{user}{bcolors.ENDC}\n")
                if saveSignal:
                    writeKeyFile(user, password)
                    print(f"{bcolors.OKGREEN}L??u t??i kho???n th??nh c??ng.{bcolors.ENDC}")
                return server

            # G???p l???i n??y th?? cho ????ng nh???p l???i
            except SMTPAuthenticationError:
                print(f"{bcolors.FAIL}T??n t??i kho???n Gmail ho???c M???t kh???u SMTP sai{bcolors.ENDC}\n")
                hasDonePasswordInput = False
                break

            # C??n c??c l???i kh??c th?? d???ng ch????ng tr??nh m???t l??c r???i th??? l???i
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
                message["Subject"] = "TH??NG TIN ??I???M DANH H???C SINH L???P {} NG??Y {}".format(name, TODAY)
                message["From"] = user
                message["To"] = recipient

                # Attach summary table
                summary = {
                    "????ng gi???": [_statuses.count("????ng gi???")],
                    "Mu???n": [_statuses.count("Mu???n")],
                    "V???ng": [_statuses.count("V???ng")]
                }
                summary = build_table(DataFrame(summary))
                message.attach(MIMEText(summary, "html"))

                # Attach detailed attendance table
                body = {
                    "STT": list(range(1, len(_statuses)+1)),
                    "T??n h???c sinh": attendanceInfos[studentNames],
                    "M?? h???c sinh": attendanceInfos[studentIDs],
                    "Ng??y sinh": attendanceInfos[birthdays],
                    "Th???i gian ??i???m danh": attendanceInfos[enterTimes],
                    "Tr???ng th??i": _statuses
                }
                body = build_table(DataFrame(body), change_color=True)
                message.attach(MIMEText(body, "html"))

                # Send mail
                server.sendmail(user, recipient, message.as_string())
                print("{}{:6s} - ???? g???i{}".format(bcolors.OKGREEN, name, bcolors.ENDC))

            else:
                print("{}{:6s} - Kh??ng t??m th???y ?????a ch??? Gmail c???a gi??o vi??n trong database{}".format(
                    bcolors.FAIL, name, bcolors.ENDC))

        else:
            print("{}{:6s} - Kh??ng c?? h???c sinh ???? ????ng k?? trong h??? th???ng{}".format(bcolors.FAIL, name, bcolors.ENDC))

    server.quit()
    print(f"\n{bcolors.OKGREEN}G???i th??ng tin ??i???m danh th??nh c??ng{bcolors.ENDC}")
    print(f"{bcolors.OKCYAN}???n ph??m b???t k??? ????? tho??t{bcolors.ENDC}")
    getch()


sendMail()
