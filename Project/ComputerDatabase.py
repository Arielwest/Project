import sqlite3
from Constants import *
from ComputerObjects import *


class ComputerDatabase:

    def __init__(self):  # Constructor
        self.__database = sqlite3.connect(DATABASE_NAME)
        self.__cursor = self.__database.cursor()
        self.__create_computers_table()

    def __create_computers_table(self):
        """
        Creates the tables if it doesn't exist
        """
        self.__cursor.execute('''CREATE TABLE if not exists Computers
        (MAC   STRING,
        IP     STRING,
        active STRING);''')
        self.__database.commit()

    def add_row(self, computer):
        """
        Inserts a new row to the table
        """
        if isinstance(computer, Computer):
            self.__cursor.execute("INSERT INTO Computers VALUES('%s','%s','%s')" % (computer.mac, computer.ip, str(computer.active)))
            self.__database.commit()
        else:
            raise ValueError

    def read(self):
        """
        Reads all the database and returns it as a list
        """
        computers = []
        self.__cursor.execute("SELECT * FROM Computers;")
        self.__database.commit()
        rows = self.__cursor.fetchall()
        for row in rows:
            computers.append(Computer(row[0], row[1], row[2] == "True"))
        return computers

    def update_state(self, computer):
        """
        Updates the state of a computer
        """
        if isinstance(computer, Computer):
            active = str(computer.active)
            self.__cursor.execute("UPDATE Computers SET active='%s' WHERE MAC='%s'" % (active, computer.mac))
            self.__database.commit()
        else:
            raise ValueError

    def close(self):
        """
        Closes itself
        """
        self.__cursor.close()
        self.__database.close()


def main():
    db = ComputerDatabase()
    data = db.read()
    for computer in data:
        print str(computer)

if __name__ == "__main__":
    main()
