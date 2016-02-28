from Constants import *
from socket import socket, gethostbyaddr, gethostbyname, gethostname, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST
from threading import Thread, Lock
from ComputerDatabase import *
from NetMap import NetMap
from time import sleep
import pythoncom
from select import select
import subprocess


class Server(object):
    def __init__(self):
        self.__address = gethostbyname(gethostname())
        self.__main_socket = socket()
        self.__database = ComputerDatabase()
        self.__database_lock = Lock()
        self.__announce_socket = socket(AF_INET, SOCK_DGRAM)
        self.gui = None
        self._connected_clients = []

    def search(self, comp_list, ip):
        for comp in comp_list:
            if comp.ip == ip:
                return True
        return False


    def start(self):
        """
        Starts the server
        """
        self.__print("Updating database...")
        current_arp = NetMap.map()
        database = self.__database.read()
        # Loop for updating the state of the computer
        for computer in database:
            computer.active = self.search(current_arp, computer.ip)
            self.__database.update_state(computer)
        # Loop for updating the database
        for computer in current_arp:
            if not self.search(database, computer.ip):
                self.__database.add_row(computer)
                database = self.__database.read()
        self.__print("Database updated.")
        network_scan_thread = Thread(target=self.__network_scan)
        network_scan_thread.setDaemon(True)
        network_scan_thread.start()
        broadcast_announce_thread = Thread(target=self.__broadcast_announce)
        broadcast_announce_thread.setDaemon(True)
        broadcast_announce_thread.start()
        self.__run()

    def __run(self):
        """
        Actual main code of the server
        """
        self.__print("Server started!")
        while True:
            to_read, to_write, error = select([self.__main_socket], [], [])
            for sock in to_read:
                if sock is self.__main_socket:
                    client_socket, client_address = self.__main_socket.accept()
                    for computer in self.__database.read():
                        if computer.ip == client_address[0]:
                            self._connected_clients.append(client_socket)

    def __broadcast_announce(self):
        """
        Runs in a thread. Announces the server's existence in the network
        """
        self.__announce_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        while True:
            self.__announce_socket.sendto(SERVER_ANNOUNCE_MESSAGE, ("<broadcast>", BROADCAST_PORT))
            sleep(ANNOUNCE_SLEEP_TIME)

    def __network_scan(self):
        """
        Scans the network
        """
        while True:
            sleep(NET_SCAN_WAIT)
            pythoncom.CoInitialize()
            current_arp = NetMap.map()
            pythoncom.CoUninitialize()
            database = ComputerDatabase()
            data = database.read()
            for computer in current_arp:
                if computer not in data:
                    database.add_row(computer)
                    data = database.read()
            database.close()

    def __print(self, data):
        print data


class Client(object):
    def __init__(self, sock, computer):
        self.socket = sock
        self.__computer = computer
        # self.name =


def main():
    server = Server()
    server.start()


if __name__ == "__main__":
    main()
