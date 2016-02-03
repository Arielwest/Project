from Constants import *
import socket
from threading import Thread
from ComputerDatabase import *
from NetMap import NetMap
from time import sleep
import subprocess


class Server(object):
    def __init__(self):
        self.__address = socket.gethostbyname(socket.gethostname())
        self.__main_socket = socket.socket()
        self.__broadcast_listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__database = ComputerDatabase()
        self.gui = None

    def start(self):
        self.__print("Updating database...")
        current_arp = NetMap.map()
        database = self.__database.read()
        for computer in current_arp:
            if not computer in database:
                self.__database.add_row(computer)
                database = self.__database.read()
        self.__print("Database updated.")
        network_scan_thread = Thread(target=self.__network_scan, args=(self,))
        network_scan_thread.start()
        network_scan_thread.setDaemon(True)
        broadcast_listen_thread = Thread(target=self.__broadcast_listen, args=(self,))
        broadcast_listen_thread.start()
        broadcast_listen_thread.setDaemon(True)
        self.__run()

    def __run(self):
        self.__print("Server started!")
        pass

    def __broadcast_listen(self):
        self.__broadcast_listen_socket.bind(('0.0.0.0', BROADCAST_PORT))
        while True:
            message, address = self.__broadcast_listen_socket.recvfrom(BUFFER_SIZE)
            if message == SERVER_SEARCH_MESSAGE:
                self.__broadcast_listen_socket.sendto(self.__address, address)

    def __network_scan(self):
        while True:
            sleep(NET_SCAN_WAIT)
            current_arp = NetMap.map()
            database = self.__database.read()
            for computer in current_arp:
                if not computer in database:
                    self.__database.add_row(computer)
                    database = self.__database.read()

    def __print(self, data):
        print data


def main():
    server = Server()
    server.start()


if __name__ == "__main__":
    main()
