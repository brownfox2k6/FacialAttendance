from db_access.init import db_access
from os import listdir, remove, rename

class StudentRepository(db_access):
    def __init__(self):
        super().__init__()
        self.create_table()
    
    def create_table(self):
        self.query("action", """
            CREATE TABLE IF NOT EXISTS students (
                student_id   TEXT(25)  PRIMARY KEY,
                student_name TEXT(50)  NOT NULL,
                class_name   TEXT(10)  NOT NULL,
                parent_email TEXT(100) NOT NULL
        )""")
    
    def delete_all_students(self):
        """
        Delete all students will also delete all face data and all attendance records
        """
        self.query("DELETE * FROM attendances")
        self.query("DELETE * FROM students")
        for file in listdir(self.face_path()):
            remove(self.face_path(file))
    
    def delete_all_students_in_class(self, class_name):
        """
        Delete all students in a class will also delete
        their face data and their attendance records
        """
        data = self.query("SELECT student_id FROM students WHERE class_name=?", (class_name, ))
        for (student_id, ) in data:
            remove(self.face_path(student_id))
            self.query("DELETE FROM attendances WHERE student_id=?", (student_id, ))
        self.query("DELETE FROM students WHERE class_name=?", (class_name, ))

    def delete_student(self, student_id):
        """
        Delete a student will also delete his face data and his attendance records
        """
        self.query("DELETE FROM students WHERE student_id=?", (student_id, ))
        self.query("DELETE FROM attendances WHERE student_id=?", (student_id, ))
        remove(self.face_path(student_id))

    def add_student(self, student_id, student_name, class_name, parent_email):
        self.query("""
            INSERT INTO students (student_id, student_name, class_name, parent_email)
                VALUES (?, ?, ?, ?)
        """, (student_id, student_name, class_name, parent_email))

    def get_student(self, student_id):
        return self.query("SELECT * FROM students WHERE student_id=?", (student_id, ))

    def get_all_students(self):
        return self.query("SELECT * FROM students;")
    
    def get_all_students_in_class(self, class_name):
        return self.query("SELECT * FROM students WHERE student_class=?", (class_name, ))
    
    def update_student(self, old_student_id, new_student_id="",
                       new_student_name="", new_class_name="", new_parent_email=""):
        _, old_student_name, old_class_name, old_parent_email = self.get_student(old_student_id)
        new_student_id = new_student_id or old_student_id
        new_student_name = new_student_name or old_student_name
        new_class_name = new_class_name or old_class_name
        new_parent_email = new_parent_email or old_parent_email
        rename(self.face_path(old_student_id), self.face_path(new_student_id))
        self.query("""
            UPDATE students
                SET student_id=?, student_name=?, class_name=?, parent_email=?
                WHERE student_id=?
        """, (new_student_id, new_student_name, new_class_name, new_parent_email, old_student_id))
