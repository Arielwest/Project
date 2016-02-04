import sqlite3
from Constants import *
from Computers import *


class ComputerDatabase:

    def __init__(self):  # Constructor
        self.database = sqlite3.connect(DATABASE_NAME)
        self.cursor = self.database.cursor()
        self.create_clients_table()

    def create_clients_table(self):
        self.cursor.execute('''CREATE TABLE if not exists Computers
        (MAC   STRING,
        IP     STRING,
        active STRING);''')
        self.database.commit()

    def add_row(self, computer):
        if isinstance(computer, Computer):
            self.cursor.execute("INSERT INTO Computers VALUES('%s','%s','%s')" % (computer.mac, computer.ip, str(computer.active)))
            self.database.commit()
        else:
            raise ValueError

    def read(self):
        computers = []
        self.cursor.execute("SELECT * FROM Computers;")
        self.database.commit()
        rows = self.cursor.fetchall()
        for row in rows:
            computers.append(Computer(row[0], row[1], row[2] == "True"))
        return computers

    def update_state(self, computer):
        if isinstance(computer, Computer):
            active = str(computer.active)
            self.cursor.execute("UPDATE Computers SET active='%s' WHERE MAC='%s'" % (active, computer.mac))
            self.database.commit()
        else:
            raise ValueError


def main():
    db = ComputerDatabase()
    data = db.read()
    for computer in data:
        print str(computer)

if __name__ == "__main__":
    main()
