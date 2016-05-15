# region ---------------------------- ABOUT ----------------------------
"""
##################################################################
# Created By: Ariel Westfried                                    #
# Date: 01/01/2016                                               #
# Name: Project - Server                                         #
# Version: 1.0                                                   #
# Windows Tested Versions: Win 7 32-bit                          #
# Python Tested Versions: 2.6 32-bit                             #
# Python Environment  : PyCharm                                  #
##################################################################
"""
# endregion

# region ---------------------------- IMPORTS ----------------------------
from Constants import *
from socket import socket, gethostbyname, gethostname, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST
from threading import Thread, Lock
from ComputerDatabase import ComputerDatabase
from NetMap import NetMap
from time import sleep
import pythoncom
from select import select
from ClientInterface import ClientInterface, ClientList, Computer
from datetime import datetime
import subprocess
from Cipher import Cipher
from os.path import exists
from os import makedirs
# endregion

# region ---------------------------- Server CLASS ----------------------------


class Server(object):
    # constructor
    def __init__(self):
        self.__address = gethostbyname(gethostname())
        self.__main_socket = socket()
        self.__database = ComputerDatabase()
        self.__database_lock = Lock()
        self.__announce_socket = socket(AF_INET, SOCK_DGRAM)
        self.running = False
        self.starting = False
        self._connected_clients = ClientList()
        self.__signature = None
        self.__public_key = None

    # starts server - updates database and starts threads
    def start(self):
        """
        Starts the server
        """
        if self.starting or self.running:
            raise NameError('Already running or starting...')
        self.starting = True
        self.__signature = Cipher.crate_signature()
        self.__public_key = Cipher()
        self.__print("Updating database...")
        pythoncom.CoInitialize()
        current_arp = NetMap.map()
        pythoncom.CoUninitialize()
        database = self.__database.read()
        # Loop for updating the state of the computer
        for computer in database:
            if computer.ip == gethostbyname(gethostname()):
                computer.active = True
                self.__database.update_state(computer)
            elif computer not in current_arp:
                computer.active = False
                self.__database.update_state(computer)
        # Loop for updating the database
        for computer in current_arp:
            if computer not in database:
                self.__database.add_row(computer)
                database = self.__database.read()
        self.__print("Database updated.")
        if not exists(DOWNLOAD_UPLOAD):
            makedirs(DOWNLOAD_UPLOAD)
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

    # the main running method of the server
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
                            new_client_thread = Thread(target=self.__new_client, args=[client_socket, computer])
                            new_client_thread.setDaemon(True)
                            new_client_thread.start()

    # handles a newly connected client
    def __new_client(self, client_socket, computer):
        key = self.__key_exchange(client_socket)
        if isinstance(key, Cipher):
            self._connected_clients.append(ClientInterface(client_socket, computer, key))

    # Operates the key exchange with client
    def __key_exchange(self, sock):
        sock.send(self.__public_key.public_key().pack())
        data = sock.recv(BUFFER_SIZE)
        key = self.__public_key.decrypt(data)
        key, his_hashed_key = key.split(IN_PACK_SEPARATOR)
        if Cipher.hash(key) == his_hashed_key:
            key = Cipher.unpack(key)
            return key

    # Has it's own thread - announces the server address to the network
    def __broadcast_announce(self):
        """
        Runs in a thread. Announces the server's existence in the network
        """
        message = SERVER_ANNOUNCE_MESSAGE
        self.__announce_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        while True:
            self.__announce_socket.sendto(message, ("<broadcast>", BROADCAST_PORT))
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
            database = self.__database.read()
            for computer in database:
                if computer.ip == gethostbyname(gethostname()):
                    computer.active = True
                    self.__database.update_state(computer)
                elif computer not in current_arp:
                    computer.active = False
                    self.__database.update_state(computer)
            for computer in current_arp:
                if computer not in database:
                    self.__database.add_row(computer)
                    database = self.__database.read()

    def __print(self, data):
        print data

    def do_action(self, computer, hour, minute, second, action):
        if isinstance(computer, Computer):
            for other_computer in self.__database.read():
                if other_computer == computer:
                    now = datetime.now()
                    my_time = datetime(now.year, now.month, now.day, int(hour), int(minute), int(second))
                    to_wait = (my_time - now).seconds
                    wait_thread = Thread(target=self.__wait_to_action, args=(to_wait, action, computer))
                    wait_thread.start()
                    return

    def do_action_now(self, computer, action):
        if isinstance(computer, Computer):
            for other_computer in self.__database.read():
                if other_computer == computer:
                    self.__wait_to_action(0, action, computer)
                    return

    def __wait_to_action(self, time_to_wait, action, computer):
        sleep(time_to_wait)
        if action == "shutdown":
            client = self.__find_client(computer)
            if isinstance(client, ClientInterface):
                self._connected_clients.remove(client)
            computer.shutdown()
        else:
            computer.wake_up()
        self.__database.update_state(computer)

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
            try:
                client.update_processes()
            except:
                self._connected_clients.remove(client)
            else:
                processes_list = [dict(NAME=process.name, PID=process.pid, PARENT_ID=process.parent_id) for process in client.processes]
                return processes_list

    def terminate_process(self, computer, processes):
        client = self.__find_client(computer)
        if isinstance(client, ClientInterface):
            try:
                result = client.terminate(processes)
            except:
                self._connected_clients.remove(client)
            else:
                return result

    def open_process(self, computer, command):
        client = self.__find_client(computer)
        if isinstance(client, ClientInterface):
            try:
                result = client.open_process(command)
            except:
                self._connected_clients.remove(client)
            else:
                return result

    def get_file(self, computer, directory):
        client = self.__find_client(computer)
        if isinstance(client, ClientInterface):
            try:
                result = client.send_files(directory)
            except:
                self._connected_clients.remove(client)
            else:
                return {
                    'NAME': directory,
                    'ITEMS': result
                }

    def delete_file(self, computer, directory):
        client = self.__find_client(computer)
        if isinstance(client, ClientInterface):
            try:
                result = client.delete_file(directory)
            except:
                self._connected_clients.remove(client)
            else:
                return result

    def create_file(self, computer, path, name):
        client = self.__find_client(computer)
        if isinstance(client, ClientInterface):
            try:
                result = client.create_file(path, name)
            except:
                self._connected_clients.remove(client)
            else:
                return result

    def and_computer(self, computer):
        if isinstance(computer, Computer):
            computer.active = False
            self.__database.add_row(computer)
            return "Computer successfully added."

    def download(self, computer, directory):
        client = self.__find_client(computer)
        if isinstance(client, ClientInterface):
            file_data = client.download(directory)
            file_name = directory.split('\\')[-1]
            file_dump = open(DOWNLOAD_UPLOAD + '\\' + file_name, 'wb+')
            file_dump.write(file_data)
            file_dump.close()
            return file_name

    def remote_desktop(self, computer_list):
        for computer in computer_list:
            subprocess.Popen(['mstsc', '/v:' + computer.ip])
# endregion

# region ---------------------------- MAIN ----------------------------


# runs server without GUI
def main():
    server = Server()
    server.start()


if __name__ == "__main__":
    main()
# endregion
