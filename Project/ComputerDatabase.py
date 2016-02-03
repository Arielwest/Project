#region ----------   ABOUT   -----------------------------
"""
##################################################################
# Created By: Liel Moalem                                        #
# Date: 25/01/2016                                               #
# Name: CameraStatus                                             #
# Version: 1.0                                                   #
# Windows Tested Versions: Win 7 64-bit                          #
# Python Tested Versions: 2.7 64-bit                             #
# Python Environment  : PyCharm                                  #
##################################################################
"""
#endregion

#region ---- Imports ----
import sqlite3
from Constants import *
from Computers import *
#endregion


class ComputerDatabase:

    def __init__(self):  # Constructor
        self.database = sqlite3.connect(DATABASE_NAME)
        self.cursor = self.database.cursor()
        self.create_clients_table()

#region ---- Table creating functions ----

    def create_clients_table(self):
        self.cursor.execute('''CREATE TABLE if not exists Computers
        (MAC   STRING,
        IP     STRING,
        active STRING);''')
        self.database.commit()

    def add_row(self, computer):
        if isinstance(computer, Computer):
            if computer.active:
                active = 1
            else:
                active = 0
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

#endregion


def main():
    db = ComputerDatabase()
    data = db.read()
    for computer in data:
        print str(computer)

if __name__ == "__main__":
    main()
