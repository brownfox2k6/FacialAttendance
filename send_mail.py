# ./send_mail.py

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP
from ssl import create_default_context
from datetime import datetime
from db_access.class_repository import ClassRepository
from db_access.attendance_repository import AttendanceRepository
from build_table import build_table
from pandas import DataFrame

abbr = ('en', 'vi')


class SendMail():
    def __init__(self, transdict, lang, date=""):
        """
        Constructor for SendMail class.
        Parameters:
            - transdict: Translation dict get from translations.json
            - lang: Language (en or vi)
            - date: Specific date to get attendance information.
                    Leave it empty to get today's attendance information.
        """
        self.transdict = transdict
        self.lang = lang
        self.trans = lambda x: self.transdict[x][abbr.index(self.lang)]
        self.date = date or datetime.today().strftime("%d/%m/%Y")
        self.attendanceRepository = AttendanceRepository()
        self.classRepository = ClassRepository()
        self.login()

    def login(self):
        try:
            self.server = SMTP(host="smtp.gmail.com", port=587)
            self.server.ehlo()
            self.server.starttls(context=create_default_context())
            self.server.ehlo()
            self.server.login("brfox2k6@gmail.com", "mqxgzwsruuccteva")
        except Exception as err:
            return err
        return True

    def build_summary(self, status_count):
        """
        Build summary table
        """
        summary = {
            self.trans("On time"): [status_count["On time"]],
            self.trans("Late"): [status_count["Late"]],
            self.trans("Absent"): [status_count["Absent"]]
        }
        return build_table(DataFrame(summary))

    def build_detail(self, attendances):
        """
        Build detailed attendance table and send attendance
        information of each student to their parents
        """
        student_names, student_ids, enter_times, statuses = [], [], [], []
        for (student_id, student_name, enter_time, status, parent_email) in attendances:
            self.send_to_parent(student_id, student_name,
                                enter_time, status, parent_email)
            student_names.append(student_name)
            student_ids.append(student_id)
            enter_times.append(enter_time)
            statuses.append(self.trans(status))
        body = {
            "#": [*range(1, len(attendances)+1)],
            self.trans("Student name"): student_names,
            self.trans("Student ID"): student_ids,
            self.trans("Enter time"): enter_times,
            self.trans("Status"): statuses
        }
        return build_table(DataFrame(body), change_color=True)

    def send_to_parent(self, student_id, student_name, enter_time, status, parent_email):
        msgs = {
            ("vi", "Late"): """Học sinh <strong>{}</strong> (Mã học sinh: <strong>{}</strong>) đã điểm danh vào lúc <strong>{}</strong>. Trạng thái: <span style="color: rgb(255, 209, 77)">Đi muộn</span>.""",
            ("vi", "On time"): """Học sinh <strong>{}</strong> (Mã học sinh: <strong>{}</strong>) đã điểm danh vào lúc <strong>{}</strong>. Trạng thái: <span style="color: rgb(140, 152, 87)">Đúng giờ</span>.""",
            ("vi", "Absent"): """Học sinh <strong>{}</strong> (Mã học sinh: <strong>{}</strong>) đã không đi học. Trạng thái: <span style="color: rgb(213, 52, 87)">Vắng</span>.""",
            ("en", "Late"): """Student <strong>{}</strong> (Student ID: <strong>{}</strong>) has entered at <strong>{}</strong>. Status: <span style="color: rgb(255, 209, 77)">Late</span>.""",
            ("en", "On time"): """Student <strong>{}</strong> (Student ID: <strong>{}</strong>) has entered at <strong>{}</strong>. Status: <span style="color: rgb(140, 152, 87)">On time</span>.""",
            ("en", "Absent"): """Student <strong>{}</strong> (Student ID: <strong>{}</strong>) has not entered. Status: <span style="color: rgb(213, 52, 87)">Absent</span>.""",
        }
        message = MIMEMultipart()
        if self.lang == "en":
            title = f"ATTENDANCE INFORMATION - {self.date} - STUDENT {student_name} - {student_id}"
        else:
            title = f"THÔNG TIN ĐIỂM DANH NGÀY {self.date} - HỌC SINH {student_name} - {student_id}"
        message["Subject"] = title
        message["From"] = "brfox2k6@gmail.com"
        message["To"] = parent_email
        body = msgs[(self.lang, status)].format(
            student_name, student_id, enter_time)
        message.attach(MIMEText(body, "html"))
        self.server.send_message(message)

    def send_data(self):
        for entity in self.classRepository.get_all_classes():
            class_name = entity.class_name
            teacher_email = entity.teacher_email
            attendances, status_count = self.attendanceRepository.get_all_attendances_in_class(
                class_name, self.date)
            message = MIMEMultipart()
            if self.lang == "en":
                title = f"CLASS {class_name} - ATTENDANCE INFORMATION - {self.date}"
            else:
                title = f"THÔNG TIN ĐIỂM DANH HỌC SINH - LỚP {class_name} - NGÀY {self.date}"
            message["Subject"] = title
            message["From"] = "brfox2k6@gmail.com"
            message["To"] = teacher_email
            summary = self.build_summary(status_count)
            message.attach(MIMEText(summary, "html"))
            detail = self.build_detail(attendances)
            message.attach(MIMEText(detail, "html"))
            self.server.send_message(message)
