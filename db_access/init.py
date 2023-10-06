# ./db_access/init.py

from sqlite3 import connect


class db_access():
    def __init__(self) -> None:
        self.conn = connect("./database/attendance.db",
                            check_same_thread=False)
        self.cursor = self.conn.cursor()

    def fetchone(self, query, *args) -> tuple:
        self.cursor.execute(query, args)
        return self.cursor.fetchone()

    def fetchall(self, query, *args) -> list[tuple]:
        self.cursor.execute(query, args)
        return self.cursor.fetchall()

    def action(self, query, *args) -> None:
        self.cursor.execute(query, args)
        self.conn.commit()

    def face_path(self, name="") -> str:
        if not name:
            return "./database/faces_data"
        if name.endswith(".pkl"):
            return f"./database/faces_data/{name}"
        return f"./database/faces_data/{name}.pkl"

    def str_to_mins(self, s) -> int:
        h, m = map(int, s.split(':'))
        return h*60 + m
