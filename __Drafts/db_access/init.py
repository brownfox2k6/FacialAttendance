from sqlite3 import connect

class db_access():
    def __init__(self):
        self.conn = connect("./database/attendance.db")
        self.cursor = self.conn.cursor()
    
    def query(self, query, args=()):
        self.cursor.execute(query, args)
        if query.startswith("SELECT"):
            return self.cursor.fetchall()
        else:
            self.conn.commit()

    def face_path(self, name=""):
        if not name:
            return "./database/faces_data"
        if name.endswith(".pkl"):
            return f"./database/faces_data/{name}"
        return f"./database/faces_data/{name}.pkl"
    
    def str_to_mins(self, s):
        h, m = map(int, s.split(':'))
        return h*60 + m
