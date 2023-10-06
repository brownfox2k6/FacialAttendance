# ./db_access/class_repository.py

from db_access.init import db_access
from os import listdir, remove
from db_access.entities import ClassEntity

class ClassRepository(db_access):
    def __init__(self) -> None:
        super().__init__()
        self.create_table()
    
    def create_table(self) -> None:
        self.action("""
            CREATE TABLE IF NOT EXISTS classes (
                class_name    TEXT PRIMARY KEY,
                start_time    TEXT NOT NULL,
                teacher_email TEXT NOT NULL
        )""")

    def delete_all_classes(self) -> None:
        """
        Delete all classes will also delete all students,
        all face data and all attendance records
        """
        self.action("DELETE * FROM classes")
        self.action("DELETE * FROM students")
        self.action("DELETE * FROM attendances")
        for file in listdir(self.face_path()):
            remove(self.face_path(file))

    def add_class(self, _class: ClassEntity) -> None:
        self.action("""
            INSERT INTO classes (class_name, start_time, teacher_email)
                VALUES (?, ?, ?)
        """, _class.class_name, _class.start_time, _class.teacher_email)

    def delete_class(self, class_name: str) -> None:
        """
        Delete a class will also delete all student
        in that class, their face data and their attendance records
        """
        data = self.fetchall("""
            SELECT student_id FROM students
                WHERE class_name=?
        """, class_name)
        if data:
            for (student_id, ) in data:
                remove(self.face_path(student_id))
                self.action("DELETE FROM attendances WHERE student_id=?", student_id)
        self.action("DELETE FROM classes WHERE class_name=?", class_name)
        self.action("DELETE FROM students WHERE class_name=?", class_name)

    def get_all_classes(self) -> list[ClassEntity]:
        return [ClassEntity(*x) for x in self.fetchall("SELECT * FROM classes")]
    
    def get_class(self, class_name: str) -> (ClassEntity | None):
        data = self.fetchone("SELECT * FROM classes WHERE class_name=?", class_name)
        if data:
            return ClassEntity(*data)
    
    def update_class(self, old_class_name, new_class_name="",
                     new_enter_time="", new_teacher_email="") -> None:
        entity = self.get_class(old_class_name)
        old_enter_time = entity.start_time
        old_teacher_email = entity.teacher_email
        new_class_name = new_class_name or old_class_name
        new_enter_time = new_enter_time or old_enter_time
        new_teacher_email = new_teacher_email or old_teacher_email
        self.action("UPDATE students SET class_name=? WHERE class_name=?",
                   new_class_name, old_class_name)
        self.action("""
            UPDATE classes
                SET class_name=?, start_time=?, teacher_email=?
                WHERE class_name=?
        """, new_class_name, new_enter_time, new_teacher_email, old_class_name)
