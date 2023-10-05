from db_access.init import db_access
from os import listdir, remove
from db_access.entities import ClassEntity

class ClassRepository(db_access):
    def __init__(self):
        super().__init__()
        self.create_table()
    
    def create_table(self):
        self.query("""
            CREATE TABLE IF NOT EXISTS classes (
                class_name    TEXT(10)  PRIMARY KEY,
                start_time    TEXT(10)  NOT NULL,
                teacher_email TEXT(100) NOT NULL
        )""")

    def delete_all_classes(self):
        """
        Delete all classes will also delete all students,
        all face data and all attendance records
        """
        self.query("DELETE * FROM classes")
        self.query("DELETE * FROM students")
        self.query("DELETE * FROM attendances")
        for file in listdir(self.face_path()):
            remove(self.face_path(file))

    def add_class(self, _class):
        self.query("""
            INSERT INTO classes (class_name, start_time, teacher_email)
                VALUES (?, ?, ?)
        """, (_class.class_name, _class.start_time, _class.teacher_email))

    def delete_class(self, class_name):
        """
        Delete a class will also delete all student
        in that class, their face data and their attendance records
        """
        data = self.query("""
            SELECT student_id FROM students
                WHERE class_name=?
        """, (class_name, ))
        if data:
            for (student_id, ) in data:
                remove(self.face_path(student_id))
                self.query("DELETE FROM attendances WHERE student_id=?", (student_id, ))
        self.query("DELETE FROM classes WHERE class_name=?", (class_name, ))
        self.query("DELETE FROM students WHERE class_name=?", (class_name, ))

    def get_all_classes(self):
        return [ClassEntity(*x) for x in self.query("SELECT * FROM classes")]
    
    def get_class(self, class_name):
        return [ClassEntity(*x) for x in self.query(
            "SELECT * FROM classes WHERE class_name=?", (class_name, ))]
    
    def update_class(self, old_class_name, new_class_name="",
                     new_enter_time="", new_teacher_email=""):
        entity = self.get_class(old_class_name)[0]
        old_enter_time = entity.start_time
        old_teacher_email = entity.teacher_email
        new_class_name = new_class_name or old_class_name
        new_enter_time = new_enter_time or old_enter_time
        new_teacher_email = new_teacher_email or old_teacher_email
        self.query("UPDATE students SET class_name=? WHERE class_name=?",
                   (new_class_name, old_class_name))
        self.query("""
            UPDATE classes
                SET class_name=?, start_time=?, teacher_email=?
                WHERE class_name=?
        """, (new_class_name, new_enter_time, new_teacher_email, old_class_name))