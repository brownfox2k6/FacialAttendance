from sqlite3 import connect
from os import listdir, remove, rename
from datetime import datetime

def face_path(name=""):
    if not name:
        return "./database/faces_data"
    if name.endswith(".pkl"):
        return f"./database/faces_data/{name}"
    return f"./database/faces_data/{name}.pkl"

def exec_query(query, args=()):
    conn = connect("./database/attendance.db")
    cursor = conn.cursor()
    cursor.execute(query, args)
    if query.startswith("SELECT"):
        data = cursor.fetchall()
        conn.close()
        return data
    else:
        conn.commit()
        conn.close()


class ClassRepository():
    def __init__(self):
        self.create_table()
    
    def create_table(self):
        exec_query("""
            CREATE TABLE IF NOT EXISTS classes (
                class_name    TEXT(10)  PRIMARY KEY,
                start_time    TEXT(10)  NOT NULL,
                teacher_email TEXT(100) NOT NULL
        )""")

    def delete_all_classes(self):
        """
        Delete all classes will also delete all students and all face data
        """
        exec_query("DELETE * FROM classes")
        exec_query("DELETE * FROM students")
        for file in listdir(face_path()):
            remove(face_path(file))

    def add_class(self, class_name, start_time, teacher_email):
        exec_query(self.execute_query("""
            INSERT INTO classes (class_name, start_time, teacher_email)
                VALUES (?, ?, ?)
        """, (class_name, start_time, teacher_email)))

    def delete_class(self, class_name):
        """
        Delete class will also delete all student
        in that class and their face data
        """
        data = exec_query("""
            SELECT student_id FROM students
                WHERE class_name=?
        """, (class_name, ))
        for (student_id, ) in data:
            remove(face_path(student_id))
        exec_query("DELETE FROM classes WHERE class_name=?", (class_name, ))
        exec_query("DELETE FROM students WHERE class_name=?", (class_name, ))

    def get_all_classes(self):
        return exec_query("SELECT * FROM classes")
    
    def get_class(self, class_name):
        return exec_query("SELECT * FROM classes WHERE class_name=?", (class_name, ))
    
    def update_class(self, old_class_name, new_class_name="",
                     new_enter_time="", new_teacher_email=""):
        _, old_enter_time, old_teacher_email = self.get_class(old_class_name)
        new_class_name = new_class_name or old_class_name
        new_enter_time = new_enter_time or old_enter_time
        new_teacher_email = new_teacher_email or old_teacher_email
        exec_query("UPDATE students SET class_name=? WHERE class_name=?",
                   (new_class_name, old_class_name))
        exec_query("""
            UPDATE classes
                SET class_name=?, enter_time=?, teacher_email=?
                WHERE class_name=?
        """, (new_class_name, new_enter_time, new_teacher_email, old_class_name))


class StudentRepository():
    def __init__(self):
        self.create_table()
    
    def create_table(self):
        exec_query("action", """
            CREATE TABLE IF NOT EXISTS students (
                student_id   TEXT(25)  PRIMARY KEY,
                student_name TEXT(50)  NOT NULL,
                class_name   TEXT(10)  NOT NULL,
                parent_email TEXT(100) NOT NULL
        )""")
    
    def delete_all_students(self):
        exec_query("DELETE * FROM students")
        for file in listdir(face_path()):
            remove(face_path(file))
    
    def delete_all_students_in_class(self, class_name):
        data = exec_query("SELECT student_id FROM students WHERE class_name=?", (class_name, ))
        for (student_id, ) in data:
            remove(face_path(student_id))
        exec_query("DELETE FROM students WHERE class_name=?", (class_name, ))

    def delete_student(self, student_id):
        exec_query("DELETE FROM students WHERE student_id=?", (student_id, ))
        remove(face_path(student_id))

    def add_student(self, student_id, student_name, class_name, parent_email):
        exec_query("""
            INSERT INTO students (student_id, student_name, class_name, parent_email)
                VALUES (?, ?, ?, ?)
        """, (student_id, student_name, class_name, parent_email))

    def get_student(self, student_id):
        return exec_query("SELECT * FROM students WHERE student_id=?", (student_id, ))

    def get_all_students(self):
        return exec_query("SELECT * FROM students;")
    
    def get_all_students_in_class(self, class_name):
        return exec_query("SELECT * FROM students WHERE student_class=?", (class_name, ))
    
    def update_student(self, old_student_id, new_student_id="",
                       new_student_name="", new_class_name="", new_parent_email=""):
        _, old_student_name, old_class_name, old_parent_email = self.get_student(old_student_id)
        new_student_id = new_student_id or old_student_id
        new_student_name = new_student_name or old_student_name
        new_class_name = new_class_name or old_class_name
        new_parent_email = new_parent_email or old_parent_email
        rename(face_path(old_student_id), face_path(new_student_id))
        exec_query("""
            UPDATE students
                SET student_id=?, student_name=?, class_name=?, parent_email=?
                WHERE student_id=?
        """, (new_student_id, new_student_name, new_class_name, new_parent_email, old_student_id))


class AttendanceRepository():
    def __init__(self):
        self.create_table()
    
    def create_table(self):
        exec_query("""
            CREATE TABLE IF NOT EXISTS attendances (
                date       TEXT(10) NOT NULL,
                student_id TEXT(15) NOT NULL,
                enter_time TEXT(10) NOT NULL
        )""")

    def reset_table(self):
        exec_query("DELETE * FROM attendances")

    def get_all_attendances(self):
        return exec_query("SELECT * FROM attendances")
    
    def add_attendance(self, student_id):
        date, time = datetime.today().strftime("%d/%m/%Y %H:%M").split()
        exec_query("INSERT INTO attendances (date, student_id, enter_time) VALUES (?, ?, ?)",
                   (date, student_id, time))
    
    def check_student_attendance(self, student_id, date=""):
        """
        Returns enter_time if this student attended, otherwise None
        """
        date = date or datetime.today().strftime("%d/%m/%Y")
        result = exec_query("SELECT enter_time FROM attendances WHERE date=? AND student_id=?",
                            (date, student_id))
        if result is not None:
            return result[0][0]

    def get_all_attendances_in_class(self, class_name, date=""):
        """
        Returns list[ tuple[ student_id, student_name, enter_time, status, parent_email ]]
        in sorted order of enter_time
        """
        def str_to_mins(s): h, m = map(int, s.split(':')); return h*60 + m
        date = date or datetime.today().strftime("%d/%m/%Y")
        students = exec_query("SELECT student_id, student_name, parent_email \
                               FROM students WHERE class_name=?", (class_name, ))
        class_enter_time = str_to_mins(exec_query(
                "SELECT start_time FROM classes WHERE class_name=?", (class_name, ))[0][0])
        attendances = {x[0]: x[1] for x in exec_query(
                "SELECT student_id, enter_time FROM attendances WHERE date=?", (date, ))}
        result = []
        for student in students:
            status = "ABSENT"
            enter_time = ""
            if student[0] in attendances:
                enter_time = attendances[student[0]]
                status = "ON_TIME" if str_to_mins(enter_time) <= class_enter_time else "LATE"
            result.append((student[0], student[1], enter_time, status, student[2]))
        return sorted(result, key=lambda x: x[2])
