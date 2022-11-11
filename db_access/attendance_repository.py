from sqlite3 import connect


class AttendanceRepository():
    def __init__(self, db_name) -> None:
        self.db_name = db_name
        self.create_table()        

    def create_table(self):
        conn = connect(self.db_name)
        query = '''
            CREATE TABLE IF NOT EXISTS attendances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day TEXT NOT NULL,
                student_id TEXT (100) NOT NULL,
                enter_time TEXT,
                exit_time TEXT,
                FOREIGN KEY(student_id) REFERENCES students(student_id)    
            );
            '''
        try:        
            cursor = conn.cursor()
            cursor.execute(query)
        except:
            print ('error in operation')
            conn.rollback()
        conn.close()

    def add_attendance(self, attendance_entity):
        conn = connect(self.db_name)
        query = '''
            INSERT INTO attendances (day, student_id, enter_time) 
            VALUES (?,?,?);
            '''
        try:        
            cursor = conn.cursor()
            cursor.execute(query, (attendance_entity.day,attendance_entity.student_id, attendance_entity.enter_time))
            conn.commit()
        except:
            print('error in operation')
            conn.rollback()
        conn.close()

    def check_student_attendance(self, student_id, day):
        conn = connect(self.db_name)
        query = '''
            SELECT COUNT(*) AS num_attendance
            FROM attendances
            WHERE attendances.student_id = ? AND attendances.day = ?;
            '''
        cursor = conn.cursor()
        cursor.execute(query, (student_id, day))
        query_result = cursor.fetchall()
        conn.close()
        return(int)(query_result[0][0]) > 0

    def get_student_enter_time(self, class_name, day):
        conn = connect(self.db_name)
        query = '''
            SELECT
                s.student_id,
                s.name AS student_name,
                s.birthday,
                c.start_time,
                sa.enter_time,
                c.name AS class_name
            FROM classes c
            LEFT JOIN students s ON s.class_id = c.id
            LEFT JOIN (
                SELECT s.student_id, a.enter_time
                FROM students s
                LEFT JOIN attendances a ON a.student_id = s.student_id
                WHERE a.day = ?
            ) AS sa ON sa.student_id = s.student_id
            WHERE c.name = ?;
            '''
        cursor = conn.cursor()
        cursor.execute(query, (day, class_name))
        query_result = cursor.fetchall()
        conn.close()
        return query_result