from db_access.init import db_access
from datetime import datetime

class AttendanceRepository(db_access):
    def __init__(self):
        super().__init__()
        self.create_table()
    
    def create_table(self):
        self.query("""
            CREATE TABLE IF NOT EXISTS attendances (
                date       TEXT(10) NOT NULL,
                student_id TEXT(15) NOT NULL,
                enter_time TEXT(10) NOT NULL
        )""")

    def reset_table(self):
        self.query("DELETE * FROM attendances")

    def get_all_attendances(self):
        return self.query("SELECT * FROM attendances")
    
    def add_attendance(self, student_id):
        date, time = datetime.today().strftime("%d/%m/%Y %H:%M").split()
        self.query("INSERT INTO attendances (date, student_id, enter_time) VALUES (?, ?, ?)",
                   (date, student_id, time))
    
    def check_student_attendance(self, student_id, date=""):
        """
        Returns enter_time if this student attended, otherwise None
        """
        date = date or datetime.today().strftime("%d/%m/%Y")
        result = self.query("SELECT enter_time FROM attendances WHERE date=? AND student_id=?",
                            (date, student_id))
        if result is not None:
            return result[0][0]

    def get_all_attendances_in_class(self, class_name, date=""):
        """
        Returns list[ tuple[ student_id, student_name, enter_time, status, parent_email ]]
        in sorted order of enter_time
        """
        date = date or datetime.today().strftime("%d/%m/%Y")
        students = self.query("SELECT student_id, student_name, parent_email \
                               FROM students WHERE class_name=?", (class_name, ))
        class_enter_time = self.str_to_mins(self.query(
                "SELECT start_time FROM classes WHERE class_name=?", (class_name, ))[0][0])
        attendances = {x[0]: x[1] for x in self.query(
                "SELECT student_id, enter_time FROM attendances WHERE date=?", (date, ))}
        result = []
        for student in students:
            status = "ABSENT"
            enter_time = ""
            if student[0] in attendances:
                enter_time = attendances[student[0]]
                status = "ON_TIME" if self.str_to_mins(enter_time) <= class_enter_time else "LATE"
            result.append((student[0], student[1], enter_time, status, student[2]))
        return sorted(result, key=lambda x: x[2])
