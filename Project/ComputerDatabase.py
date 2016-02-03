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
        # self.create_classification_table()
        self.create_clients_table()
        # self.create_process_table()

#region ---- Table creating functions ----

    def create_clients_table(self):
        self.database.execute('''CREATE TABLE if not exists Computers
        (MAC          STRING   NOT NULL,
        IP            STRING   NOT NULL,
        computer_name STRING   NOT NULL);''')

    """"
    def create_process_table(self):
        self.database.execute('''CREATE TABLE Processes
        (Process_ID INT PRIMARY KET NOT NULL,
        Process_name STRING NOT NULL,
        Process_size INT NOT NULL);''')

    def create_classification_table(self):
        self.database.execute('''CREATE TABLE Classification
        (Classification_ID INT PRIMARY KEY NOT NULL,
        Client_name STRING NOT NULL,
        Process_ID INT NOT NULL,
        Classification INT NOT NULL,
        Notes STRING);''')
    """

    def add_row(self, computer):
        self.database.execute("INSERT INTO Computers (MAC, IP, computer_name) VALUES ('%s','%s','%s')" %(computer.mac, computer.ip, computer.computer_name))

    def is_exist(self, computer):
        pass

    def read(self):
        answer = self.database.execute("SELECT * FROM Computers;")
        computers = []
        for row in answer:
            computers.append(Computer(row[0], row[1], row[2]))
        return computers


#endregion


def main():
    db = ComputerDatabase()
    data = db.read()
    for computer in data:
        print computer

if __name__ == "__main__":
    main()