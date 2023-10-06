# ./utilities.py

from colorama import init, Fore, Back, Style
from sqlite3 import connect
from json import load, dump
from PyQt6.QtMultimedia import QMediaDevices
from db_access.class_repository import ClassRepository
from db_access.student_repository import StudentRepository
from db_access.entities import ClassEntity
from tabulate import tabulate
from send_mail import SendMail
from datetime import datetime

abbr = ("", "en", "vi")
full = ("", "English", "Vietnamese")


class Utilities():
    def __init__(self):
        init(autoreset=True)
        self.get_available_webcams = lambda: [
            '.'+x.description() for x in QMediaDevices.videoInputs()]
        self.get_configurations()
        self.get_translations()
        self.classRepository = ClassRepository()
        self.studentRepository = StudentRepository()

    def get_configurations(self):
        with open("./resources/configurations.json") as f:
            self.configurations = load(f)

    def save_configurations(self):
        with open("./resources/configurations.json", "w") as f:
            dump(self.configurations, f)

    def change_webcam(self, new_webcam):
        self.configurations["webcam"] = new_webcam

    def get_current_webcam(self):
        return self.get_available_webcams()[self.configurations["webcam"]]

    def get_translations(self):
        conn = connect("./resources/translations.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM translations")
        self.transdict = {x[0]: x for x in cursor.fetchall()}
        self.trans = lambda x: x[1:] if x[0] == '.' else\
            self.transdict[x][abbr.index(self.configurations["lang"])-1]
        conn.close()

    def main(self):
        options = ("Change language", "Change webcam", "Options - Classes",
                   "Options - Students", "Send attendance records")
        self.print_options("Facial attendance system", *options)
        match self.get_choice(len(options)):
            case 0: exit()
            case 1: self.change_lang()
            case 2: self.change_webcam()
            case 3: self.work_with_classes()
            case 4: self.work_with_students()
            case 5: self.send_attendance_records()

    def change_lang(self):  # Option 1 of main (1)
        options = ("English", "Vietnamese", )
        self.print_options("Change language", "English", "Vietnamese")
        if choice := self.get_choice(len(options)):
            old = full[abbr.index(self.configurations["lang"])]
            self.configurations["lang"] = abbr[choice]
            self.change("Language changed", old, full[choice])
        self.main()

    def change_webcam(self):  # Option 2 of main (2)
        options = self.get_available_webcams()
        self.print_options("Change webcam", *options)
        old = self.get_current_webcam()
        print(f'{Fore.YELLOW}{self.trans("Current webcam")}: {self.trans(old)}')
        if choice := self.get_choice(len(options)):
            choice -= 1
            new = options[choice]
            self.configurations["webcam"] = choice
            self.change("Webcam changed", old, new)
        self.main()

    def work_with_classes(self):  # Option 3 of main (3)
        while True:
            classes = self.classRepository.get_all_classes()
            table = {
                '#': [*range(1, len(classes)+1)],
                self.trans("Class"): [],
                self.trans("Start time"): [],
                self.trans("Teacher's email"): []
            }
            for _class in classes:
                table[self.trans("Class")].append(_class.class_name)
                table[self.trans("Start time")].append(_class.start_time)
                table[self.trans("Teacher's email")].append(
                    _class.teacher_email)

            print(
                f'\n{Style.BRIGHT}{Fore.MAGENTA}{Back.CYAN}{self.trans("Classes")}')
            print(tabulate(table, headers="keys", tablefmt="grid"))
            options = ("Add class", "Delete class", "Modify class")
            self.print_options('', *options)
            match self.get_choice(len(options)):
                case 0: self.main()
                case 1: self.add_class()
                case 2: self.delete_class(table)
                case 3: self.modify_class(table)

    def add_class(self):  # Option 1 of work_with_classes (3.1)
        print(
            f'\n{Style.BRIGHT}{Fore.MAGENTA}{Back.CYAN}{self.trans("Classes")} -> {self.trans("Add class")}')
        print(f'{Fore.CYAN}>>> {self.trans("Class (e.g. 10A1)")}:  ', end='')
        class_name = input().upper()
        print(f'{Fore.CYAN}>>> {self.trans("Start time")} (HH:MM):  ', end='')
        start_time = input()
        print(
            f"""{Fore.CYAN}>>> {self.trans("Teacher's email (e.g. abc@gmail.com)")}:  """, end='')
        teacher_email = input()
        print(f"""{Fore.YELLOW}{self.trans("[!] Please make sure this information is valid "
                                           "and correct, do you want to proceed (y/n)?")}  """, end='')
        if self.get_yn():
            self.classRepository.add_class(ClassEntity(
                class_name, start_time, teacher_email))
            print(f'{Fore.GREEN}{self.trans("Operation completed!")}')
        else:
            print(f'{Fore.RED}{self.trans("Operation aborted.")}')

    def delete_class(self, table):  # Option 2 of work_with_classes (3.2)
        print(
            f'\n{Style.BRIGHT}{Fore.MAGENTA}{Back.CYAN}{self.trans("Classes")} -> {self.trans("Delete class")}')
        print(f"""{Fore.CYAN}{self.trans(">>> Enter indexes of class(es) you want "
                                         "to delete (separated by spaces)")} (1-{len(table["#"])}):  """, end='')
        while True:
            try:
                classes = [table[self.trans("Class")][int(x)-1]
                           for x in input().split()]
                break
            except:
                print(
                    f'{Fore.RED}{self.trans(">>> Invalid choice, please choose again")} (1-{len(table["#"])}):  ', end='')
        print(f"""{Fore.YELLOW}{self.trans("[!] Delete a class will also delete all students in that class, "
                                           "all their face data as well as their attendance records, "
                                           "do you want to proceed (y/n)?")}  """, end='')
        if self.get_yn():
            for _class in classes:
                self.classRepository.delete_class(_class)
            print(
                f'{Fore.GREEN}{self.trans("Operation completed!")} (Deleted {", ".join(classes)})')
        else:
            print(f'{Fore.RED}{self.trans("Operation aborted.")}')
        self.work_with_classes()

    def modify_class(self, table):  # Option 3 of work_with_classes (3.3)
        print(
            f'\n{Style.BRIGHT}{Fore.MAGENTA}{Back.CYAN}{self.trans("Classes")} -> {self.trans("Modify class")}')
        idx = self.get_choice(
            len(table["#"]), 1, ">>> Enter index of a class you want to modify") - 1
        old_class_name = table[self.trans("Class")][idx]
        old_start_time = table[self.trans("Start time")][idx]
        old_teacher_email = table[self.trans("Teacher's email")][idx]
        print(f'{Fore.CYAN}>>> {self.trans("Enter new class name")} ({self.trans("current")}: '
              f'{old_class_name}, {self.trans("leave empty to keep it unchanged")}):  ', end='')
        class_name = input() or old_class_name
        print(f'{Fore.CYAN}>>> {self.trans("Enter new start time (HH:MM)")} ({self.trans("current")}: '
              f'{old_start_time}, {self.trans("leave empty to keep it unchanged")}):  ', end='')
        start_time = input() or old_start_time
        print(f"""{Fore.CYAN}>>> {self.trans("Enter new teacher's email (e.g. abc@gmail.com)")} ({self.trans("current")}: """
              f'{old_teacher_email}, {self.trans("leave empty to keep it unchanged")}):  ', end='')
        teacher_email = input() or old_teacher_email
        print(f"""{Fore.YELLOW}{self.trans("[!] Please make sure this information is valid "
                                           "and correct, do you want to proceed (y/n)?")}  """, end='')
        if self.get_yn():
            self.classRepository.update_class(
                old_class_name, class_name, start_time, teacher_email)
            print(f'{Fore.GREEN}{self.trans("Operation completed!")}')
            print(
                f'{Fore.GREEN}{self.trans("Class")}: {old_class_name} -> {class_name}')
            print(
                f'{Fore.GREEN}{self.trans("Start time")}: {old_start_time} -> {start_time}')
            print(
                f"""{Fore.GREEN}{self.trans("Teacher's email")}: {old_teacher_email} -> {teacher_email}""")
        else:
            print(f'{Fore.RED}{self.trans("Operation aborted.")}')
        self.work_with_classes()

    def work_with_students(self):  # Option 4 of main (4)
        print(f'\n{Style.BRIGHT}{Fore.MAGENTA}{Back.CYAN}{self.trans("Students")}')
        print(f'{Fore.CYAN}>>> {self.trans("Class (e.g. 10A1)")}:  ', end='')
        class_name = input().upper()
        if not self.classRepository.get_class(class_name):
            print(
                f'{Fore.RED}{self.trans("This class does not exist. Please create it first.")}')
            return
        students = self.studentRepository.get_all_students_in_class(class_name)
        if not students:
            print(f'{Fore.RED}{self.trans("This class has no students.")}')
            return
        table = {
            '#': [*range(1, len(students)+1)],
            self.trans('Full name'): [],
            self.trans('Student ID'): [],
            self.trans("Parent's email"): []
        }
        for entity in students:
            table[self.trans('Full name')].append(entity.student_name)
            table[self.trans('Student ID')].append(entity.student_id)
            table[self.trans("Parent's email")].append(entity.parent_email)
        print(
            f'\n{Style.BRIGHT}{Fore.MAGENTA}{Back.CYAN}{self.trans("Students")} -> {class_name}')
        print(tabulate(table, headers="keys", tablefmt="grid"))
        options = ("Modify a student", "Delete student(s)")
        self.print_options('', *options)
        match self.get_choice(len(options)):
            case 0: self.main()
            case 1: self.modify_student(class_name, table)
            case 2: self.delete_student(class_name, table)

    def modify_student(self, _class, table):  # Option 1 of work_with_students (4.1)
        print(f'\n{Style.BRIGHT}{Fore.MAGENTA}{Back.CYAN}{self.trans("Students")} -> {_class} -> {self.trans("Modify a student")}')
        idx = self.get_choice(
            len(table["#"]), 1, ">>> Enter index of a student you want to modify") - 1
        old_id = table[self.trans("Student ID")][idx]
        old_name = table[self.trans("Full name")][idx]
        old_email = table[self.trans("Parent's email")][idx]
        old_class = _class
        print(f'{Fore.CYAN}>>> {self.trans("Enter new student ID")} ({self.trans("current")}: '
              f'{old_id}, {self.trans("leave empty to keep it unchanged")}):  ', end='')
        new_id = input() or old_id
        print(f'{Fore.CYAN}>>> {self.trans("Enter new student name")} ({self.trans("current")}: '
              f'{old_name}, {self.trans("leave empty to keep it unchanged")}):  ', end='')
        new_name = input() or old_name
        print(f'{Fore.CYAN}>>> {self.trans("Enter new class")} ({self.trans("current")}: '
              f'{old_class}, {self.trans("leave empty to keep it unchanged")}):  ', end='')
        new_class = input() or old_class
        print(f"""{Fore.CYAN}>>> {self.trans("Enter new parent's email")} ({self.trans("current")}: """
              f"""{old_email}, {self.trans("leave empty to keep it unchanged")}):  """, end='')
        new_email = input() or old_email
        print(f"""{Fore.YELLOW}{self.trans("[!] Please make sure this information is valid "
                                           "and correct, do you want to proceed (y/n)?")}  """, end='')
        if self.get_yn():
            self.studentRepository.update_student(
                old_id, new_id, new_name, new_class, new_email)
            print(f'{Fore.GREEN}{self.trans("Operation completed!")}')
            print(f'{Fore.GREEN}{self.trans("Student ID")}: {old_id} -> {new_id}')
            print(f'{Fore.GREEN}{self.trans("Full name")}: {old_name} -> {new_name}')
            print(f'{Fore.GREEN}{self.trans("Class")}: {old_class} -> {new_class}')
            print(
                f"""{Fore.GREEN}{self.trans("Parent's email")}: {old_email} -> {new_email}""")
        else:
            print(f'{Fore.RED}{self.trans("Operation aborted.")}')
        self.work_with_students()

    def delete_student(self, _class, table):  # Option 2 of work_with_students (4.2)
        print(f'\n{Style.BRIGHT}{Fore.MAGENTA}{Back.CYAN}{self.trans("Students")} -> {_class} -> {self.trans("Delete student(s)")}')
        print(f"""{Fore.CYAN}{self.trans(">>> Enter indexes of student(s) you want "
                                         "to delete (separated by spaces)")} (1-{len(table["#"])}):  """, end='')
        while True:
            try:
                students = [table[self.trans("Student ID")][int(x)-1]
                            for x in input().split()]
                break
            except:
                print(
                    f'{Fore.RED}{self.trans(">>> Invalid choice, please choose again")} (1-{len(table["#"])}):  ', end='')
        print(f"""{Fore.YELLOW}{self.trans("[!] Delete a student will also delete his/her face data"
                                           "as well as his/her attendance records, do you want to proceed (y/n)?")}  """, end='')
        if self.get_yn():
            for student in students:
                self.studentRepository.delete_student(student)
            print(
                f'{Fore.GREEN}{self.trans("Operation completed!")} (Deleted {", ".join(students)})')
        else:
            print(f'{Fore.RED}{self.trans("Operation aborted.")}')
        self.work_with_students()

    def send_attendance_records(self):
        print(
            f'\n{Style.BRIGHT}{Fore.MAGENTA}{Back.CYAN}{self.trans("Send attendance records")}')
        print(f"""{Fore.CYAN}{self.trans(">>> Enter date (leave empty to send today's records) (dd/mm/yyyy)")}:  """, end='')
        while True:
            try:
                inp = input()
                if not inp:
                    dt = datetime.today().strftime("%d/%m/%Y")
                else:
                    d, m, y = map(int, inp.split('/'))
                    dt = datetime(y, m, d).strftime("%d/%m/%Y")
                break
            except:
                print(
                    f'{Fore.RED}{self.trans(">>> Invalid date, please enter again")}:  ', end='')
        sendMail = SendMail(self.transdict, self.configurations["lang"], dt)
        sendMail.send_data()
        print(f'{Fore.GREEN}{self.trans("Data sent successfully!")} ({dt})')
        self.main()

    def print_options(self, title, *options):
        # Print title
        if title:
            print(f'\n{Style.BRIGHT}{Fore.MAGENTA}{Back.CYAN}{self.trans(title)}')
        # Print available options
        print(f'{Fore.YELLOW}{self.trans("Options")}\n==========')
        print(f'{Fore.YELLOW}0 - ({self.trans("Return")})')
        for idx, option in enumerate(options, 1):
            print(f'{Fore.YELLOW}{idx} - {self.trans(option)}')
        print(f'{Fore.YELLOW}==========')

    def get_choice(self, r, l=0, s=">>> Your choice"):
        print(f'{Fore.CYAN}{self.trans(s)} ({l}-{r}):  ', end='')
        while True:
            try:
                choice = int(input())
                if l <= choice <= r:
                    return choice
                raise ValueError
            except:
                print(
                    f'{Fore.RED}{self.trans(">>> Invalid choice, please choose again")} ({l}-{r}):  ', end='')

    def get_yn(self):
        while True:
            match input().strip().lower():
                case 'y': return True
                case 'n': return False
            print(
                f'{Fore.RED}{self.trans(">>> Invalid choice, please choose again")} (y/n):  ', end='')

    def change(self, announce, old, new):
        print(
            f'{Fore.GREEN}{self.trans(announce)} ({self.trans(old)} -> {self.trans(new)})')
        self.save_configurations()


a = Utilities()
a.main()
