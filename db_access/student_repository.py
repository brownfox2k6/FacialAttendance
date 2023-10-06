# ./db_access/student_repository.py

from os import listdir, remove, rename
from db_access.entities import StudentEntity
from db_access.init import db_access


class StudentRepository(db_access):
    def __init__(self):
        super().__init__()
        self.create_table()

    def create_table(self) -> None:
        self.action("""
            CREATE TABLE IF NOT EXISTS students (
                student_id   TEXT PRIMARY KEY,
                student_name TEXT NOT NULL,
                class_name   TEXT NOT NULL,
                parent_email TEXT NOT NULL
        )""")

    def delete_all_students(self) -> None:
        """
        Delete all students will also delete all face data and all attendance records
        """
        self.action("DELETE * FROM attendances")
        self.action("DELETE * FROM students")
        for file in listdir(self.face_path()):
            remove(self.face_path(file))

    def delete_all_students_in_class(self, class_name: str) -> None:
        """
        Delete all students in a class will also delete
        their face data and their attendance records
        """
        data = self.fetchall(
            "SELECT student_id FROM students WHERE class_name=?", class_name)
        for (student_id, ) in data:
            remove(self.face_path(student_id))
            self.action(
                "DELETE FROM attendances WHERE student_id=?", student_id)
        self.action("DELETE FROM students WHERE class_name=?", class_name)

    def delete_student(self, student_id: str) -> None:
        """
        Delete a student will also delete his face data and his attendance records
        """
        self.action("DELETE FROM students WHERE student_id=?", student_id)
        self.action("DELETE FROM attendances WHERE student_id=?", student_id)
        remove(self.face_path(student_id))

    def add_student(self, student: StudentEntity) -> None:
        self.query("""
            INSERT INTO students (student_id, student_name, class_name, parent_email)
                VALUES (?, ?, ?, ?)
        """, student.student_id, student.student_name, student.class_name, student.parent_email)

    def get_student(self, student_id: str) -> (StudentEntity | None):
        data = self.fetchone(
            "SELECT * FROM students WHERE student_id=?", student_id)
        if data:
            return StudentEntity(*data)

    def get_all_students(self) -> list[StudentEntity]:
        return [StudentEntity(*x) for x in self.fetchall("SELECT * FROM students")]

    def get_all_students_in_class(self, class_name) -> list[StudentEntity]:
        return [StudentEntity(*x) for x in self.fetchall(
            "SELECT * FROM students WHERE class_name=?", class_name)]

    def update_student(self, old_student_id, new_student_id="",
                       new_student_name="", new_class_name="", new_parent_email="") -> None:
        student = self.get_student(old_student_id)
        old_student_name = student.student_name
        old_class_name = student.class_name
        old_parent_email = student.parent_email
        new_student_id = new_student_id or old_student_id
        new_student_name = new_student_name or old_student_name
        new_class_name = new_class_name or old_class_name
        new_parent_email = new_parent_email or old_parent_email
        rename(self.face_path(old_student_id), self.face_path(new_student_id))
        self.action("""
            UPDATE students
                SET student_id=?, student_name=?, class_name=?, parent_email=?
                WHERE student_id=?
        """, new_student_id, new_student_name, new_class_name, new_parent_email, old_student_id)
        self.action("""
            UPDATE attendances
                SET student_id=?
                WHERE student_id=?
        """, new_student_id, old_student_id)
