import socket
from uuid import getnode as get_mac
from Constants import *
import re
from threading import Thread, Lock


class Client(object):
    def __init__(self):
        self.__socket = socket.socket()
        self.__mac = get_mac()
        self.__name = socket.gethostname()

    def __print(self, data):
        print data

    def start(self):
        self.__print("connecting")
        is_server = self.__find_server()
        if is_server:
            print "connected to server."
            self.__run()
        else:
            print "server not found."

    def __find_server(self):
        search_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        search_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        search_socket.sendto(SERVER_SEARCH_MESSAGE, ("<broadcast>", BROADCAST_PORT))
        del search_socket
        search_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        search_socket.bind(("0.0.0.0", BROADCAST_PORT))
        server_address = search_socket.recvfrom(BUFFER_SIZE)
        if is_ip(server_address):
            status = self.__socket.connect_ex((server_address, SERVER_PORT))
            if status == 0:
                return True
        return False

    def __run(self):
        pass

    def __update_data(self):
        pass


def is_ip(ip):
    return re.match(IP_REGULAR_EXPRESSION, ip)


def main():
    client = Client()
    client.start()


if __name__ == "__main__":
    main()