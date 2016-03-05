from Constants import *
from socket import socket, gethostbyname, gethostname, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST
from threading import Thread, Lock
from ComputerDatabase import ComputerDatabase
from NetMap import NetMap
from time import sleep
import pythoncom
from select import select
from ClientInterface import ClientInterface, ClientList, Computer


class Server(object):
    def __init__(self):
        self.__address = gethostbyname(gethostname())
        self.__main_socket = socket()
        self.__database = ComputerDatabase()
        self.__database_lock = Lock()
        self.__announce_socket = socket(AF_INET, SOCK_DGRAM)
        self.running = False
        self.starting = False
        self._connected_clients = ClientList()

    def search(self, comp_list, ip):
        for comp in comp_list:
            if comp.ip == ip:
                return True
        return False

    def start(self):
        """
        Starts the server
        """
        self.starting = True
        self.__print("Updating database...")
        pythoncom.CoInitialize()
        current_arp = NetMap.map()
        pythoncom.CoUninitialize()
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
        self.__main_socket.bind(("0.0.0.0", SERVER_PORT))
        self.__main_socket.listen(1)
        self.starting = False
        self.running = True
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
                            self._connected_clients.append(ClientInterface(client_socket, computer))

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
            data = self.__database.read()
            for computer in current_arp:
                if computer not in data:
                    self.__database.add_row(computer)
                    data = self.__database.read()

    def __print(self, data):
        print data

    def wake_up(self, computer):
        if isinstance(computer, Computer):
            for other_computer in self.__database.read():
                if other_computer == computer:
                    computer.wake_up()
                    self.__database.update_state(computer)
                    return

    def shutdown(self, computer):
        if isinstance(computer, Computer):
            for other_computer in self.__database.read():
                if other_computer == computer:
                    computer.shutdown()
                    self.__database.update_state(computer)
                    return

    def make_computers_dictionary(self):
        dictionary = self.__database.make_dictionary()
        dictionary["CONNECTED"] = []
        for i in xrange(len(dictionary["MAC"])):
            dictionary["CONNECTED"].append(str(Computer(dictionary["MAC"][i], dictionary["IP"][i]) in self._connected_clients))
        return dictionary

    def __find_client(self, computer):
        for client in self._connected_clients:
            if computer == client:
                return client

    def computer_data(self, computer):
        client = self.__find_client(computer)
        return {"MAC": client.get_mac(),
                "IP": client.get_ip(),
                "HOST": client.name}

    def get_processes_data(self, computer):
        client = self.__find_client(computer)
        if isinstance(client, ClientInterface):
            client.update_processes()
            processes_list = [dict(NAME=process.name, PID=process.pid, PARENT_ID=process.parent_id) for process in client.processes]
            return processes_list

    def terminate_process(self, computer, process):
        client = self.__find_client(computer)
        if isinstance(client, ClientInterface):
            result = client.terminate(process)
            return result

    def open_process(self, computer, command):
        client = self.__find_client(computer)
        if isinstance(client, ClientInterface):
            result = client.open_process(command)
            return result

    def files(self, computer):
        client = self.__find_client(computer)
        if isinstance(client, ClientInterface):
            result = client.send_files()
            return result


def main():
    server = Server()
    server.start()


if __name__ == "__main__":
    main()
