# ./db_access/attendance_repository.py

from db_access.init import db_access
from datetime import datetime


class AttendanceRepository(db_access):
    def __init__(self):
        super().__init__()
        self.create_table()

    def create_table(self) -> None:
        self.action("""
            CREATE TABLE IF NOT EXISTS attendances (
                date       TEXT NOT NULL,
                student_id TEXT NOT NULL,
                enter_time TEXT NOT NULL
        )""")

    def reset_table(self) -> None:
        self.action("DELETE * FROM attendances")

    def add_attendance(self, student_id: str) -> None:
        date, time = datetime.today().strftime("%d/%m/%Y %H:%M").split()
        self.action("INSERT INTO attendances (date, student_id, enter_time) VALUES (?, ?, ?)",
                    date, student_id, time)

    def check_student_attendance(self, student_id: str, date="") -> (str | None):
        """
        Returns enter_time if this student attended, otherwise None
        """
        date = date or datetime.today().strftime("%d/%m/%Y")
        result = self.fetchone("SELECT enter_time FROM attendances WHERE date=? AND student_id=?",
                               date, student_id)
        if result:
            return result[0]

    def get_all_attendances_in_class(self, class_name: str, date="") \
            -> tuple[list[tuple[str, str, str, str, str]], dict]:
        """
        Returns:
        - list[ tuple[ student_id, student_name, enter_time, status, parent_email ]]
        in sorted order of enter_time
        - dict[ on_time, late, absent]: summary
        """
        date = date or datetime.today().strftime("%d/%m/%Y")
        students = self.fetchall("SELECT student_id, student_name, parent_email \
                                  FROM students WHERE class_name=?", class_name)
        class_start_time = self.str_to_mins(self.fetchone(
            "SELECT start_time FROM classes WHERE class_name=?", class_name)[0])
        attendances = {x[0]: x[1] for x in self.fetchall(
            "SELECT student_id, enter_time FROM attendances WHERE date=?", date)}
        result = []
        count_status = {"On time": 0, "Late": 0, "Absent": 0}
        for student in students:
            status = "Absent"
            enter_time = ""
            if student[0] in attendances:
                enter_time = attendances[student[0]]
                status = "On time" if self.str_to_mins(
                    enter_time) <= class_start_time else "Late"
            result.append(
                (student[0], student[1], enter_time, status, student[2]))
            count_status[status] += 1
        return sorted(result, key=lambda x: x[2]), count_status

    def get_student_status(self, student_id: str) -> str:
        class_name = self.fetchone(
            "SELECT class_name FROM students WHERE student_id=?", student_id)[0]
        class_enter_time = self.fetchone(
            "SELECT start_time FROM classes WHERE class_name=?", class_name)[0]
        time = datetime.today().strftime("%H:%M")
        if self.str_to_mins(time) <= self.str_to_mins(class_enter_time):
            return "On time"
        return "Late"
