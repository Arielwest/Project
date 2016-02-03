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
        self.__announce_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.gui = None

    def start(self):
        self.__print("Updating database...")
        current_arp = NetMap.map()
        database = self.__database.read()
        for computer in database:
            if not computer in current_arp:
                computer.active = False
                self.__database.update_state(computer)
        for computer in current_arp:
            if not computer in database:
                self.__database.add_row(computer)
                database = self.__database.read()
        self.__print("Database updated.")
        exit()
        network_scan_thread = Thread(target=self.__network_scan)
        network_scan_thread.setDaemon(True)
        network_scan_thread.start()
        broadcast_announce_thread = Thread(target=self.__broadcast_announce)
        broadcast_announce_thread.setDaemon(True)
        broadcast_announce_thread.start()
        self.__run()

    def __run(self):
        self.__print("Server started!")

    def __broadcast_announce(self):
        self.__announce_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while True:
            self.__announce_socket.sendto(SERVER_ANNOUNCE_MESSAGE, ("<broadcast>", BROADCAST_PORT))
            sleep(ANNOUNCE_SLEEP_TIME)

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
