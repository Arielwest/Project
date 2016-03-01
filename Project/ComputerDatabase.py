import sqlite3
from Constants import *
from ClientInterface import Computer
import re


class ComputerDatabase:

    def __init__(self):  # Constructor
        self.__create_computers_table()

    def __create_computers_table(self):
        """
        Creates the tables if it doesn't exist
        """
        database, cursor = self.__open()
        cursor.execute('''CREATE TABLE if not exists Computers
        (MAC   STRING,
        IP     STRING,
        active STRING);''')
        database.commit()
        self.__close(cursor, database)

    def add_row(self, computer):
        """
        Inserts a new row to the table
        """
        if isinstance(computer, Computer):
            database, cursor = self.__open()
            cursor.execute("INSERT INTO Computers VALUES('%s','%s','%s')" % (computer.mac, computer.ip, str(computer.active)))
            database.commit()
            self.__close(cursor, database)
        else:
            raise ValueError

    def read(self):
        """
        Reads all the database and returns it as a list
        """
        database, cursor = self.__open()
        computers = []
        cursor.execute("SELECT * FROM Computers ORDER BY active DESC")
        database.commit()
        rows = cursor.fetchall()
        for row in rows:
            computers.append(Computer(row[0], row[1], row[2] == u"True" or row[2] == "True"))
        self.__close(cursor, database)
        return computers

    def update_state(self, computer):
        """
        Updates the state of a computer
        """
        database, cursor = self.__open()
        if isinstance(computer, Computer):
            active = str(computer.active)
            cursor.execute("UPDATE Computers SET active='%s' WHERE MAC='%s'" % (active, computer.mac))
            database.commit()
            self.__close(cursor, database)
            return
        elif (isinstance(computer, str) or isinstance(computer, unicode)) and re.match(IP_REGULAR_EXPRESSION, computer):
            parameter = "IP"
        elif (isinstance(computer, str) or isinstance(computer, unicode)) and re.match(MAC_REGULAR_EXPRESSION, computer):
            parameter = "MAC"
        else:
            raise ValueError
        cursor.execute("SELECT active FROM Computers WHERE %s='%s'" % (parameter, computer))
        database.commit()
        active = cursor.fetchone()
        active = active == u"True" or "True"
        active = not active
        cursor.execute("UPDATE Computers SET active='%s' WHERE %s='%s'" % (active, parameter, computer))
        database.commit()
        self.__close(cursor, database)


    def make_dictionary(self):
        computers_dict = {"IP": [], "MAC": [], "STATUS": [], "INDEX": []}
        computers = self.read()
        i = 1
        for computer in computers:
            computers_dict["IP"].append(computer.ip)
            computers_dict["MAC"].append(computer.mac)
            computers_dict["STATUS"].append( "online" if computer.active else "offline")
            computers_dict["INDEX"].append(i)
            i += 1
        return computers_dict


    def __close(self, cursor, database):
        """
        Closes itself
        """
        cursor.close()
        database.close()

    def __open(self):
        database = sqlite3.connect(DATABASE_NAME)
        cursor = database.cursor()
        return database, cursor


def main():
    db = ComputerDatabase()
    data = db.read()
    for computer in data:
        print str(computer)

if __name__ == "__main__":
    main()
