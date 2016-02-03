from Constants import *
import socket
from threading import Thread
from ComputerDatabase import *
from NetMap import NetMap
from Computers import *


class Server(object):
    def __init__(self):
        self.__address = socket.gethostbyname(socket.gethostname())
        self.__main_socket = socket.socket()
        self.__broadcast_listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__database = ComputerDatabase()

    def start(self):
        self.__print("Updating database...")
        list1 = NetMap.map()
        list2 = self.__database.read()
        for computer in list1:
            if not computer in list2:
                self.__database.add_row(computer)
        exit()
        self.__print("Database updated.")

        broadcast_listen_thread = Thread(target=self.__broadcast_listen, args=(self))
        broadcast_listen_thread.start()
        self.__run()

    def __run(self):
        pass

    def __broadcast_listen(self):
        self.__broadcast_listen_socket.bind(('0.0.0.0', BROADCAST_PORT))
        message, address = self.__broadcast_listen_socket.recvfrom(BUFFER_SIZE)
        if message == SERVER_SEARCH_MESSAGE:
            self.__broadcast_listen_socket.sendto(self.__address, address)

    def __print(self, data):
        print data


def main():
    server = Server()
    server.start()


if __name__ == "__main__":
    main()
