from dataclasses import dataclass

@dataclass
class ClassEntity():
    class_name: str
    start_time: str
    teacher_email: str

@dataclass
class StudentEntity():
    student_id: str
    student_name: str
    class_name: str
    parent_email: str

@dataclass
class AttendanceEntity():
    date: str
    student_id: str
    enter_time: str