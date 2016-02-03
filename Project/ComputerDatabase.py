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
        # self.create_classification_table()
        self.create_clients_table()
        # self.create_process_table()

#region ---- Table creating functions ----

    def create_clients_table(self):
        self.cursor.execute('''CREATE TABLE if not exists Computers
        (MAC          STRING,
        IP            STRING,
        computer_name STRING);''')
        self.database.commit()

    def add_row(self, computer):
        self.cursor.execute("INSERT INTO Computers VALUES('%s','%s','%s')" % (computer.mac, computer.ip, computer.computer_name))
        self.database.commit()

    def read(self):
        computers = []
        self.cursor.execute("SELECT * FROM Computers;")
        self.database.commit()
        rows = self.cursor.fetchall()
        for row in rows:
            computers.append(Computer(row[0], row[1], row[2]))
        return computers


#endregion


def main():
    db = ComputerDatabase()
    data = db.read()
    for computer in data:
        print str(computer)

if __name__ == "__main__":
    main()
