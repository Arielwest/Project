from Constants import *
from socket import gethostbyaddr
from WakeOnLan import wake_on_lan, shutdown
from Process import Process
from socket import socket
from Cipher import Cipher


class ClientInterface(object):
    def __init__(self, sock, computer, key):
        self.__socket = sock
        self.__key = key
        if not isinstance(computer, Computer):
            raise ValueError
        else:
            self.__computer = computer
            self.name = gethostbyaddr(computer.ip)[0]
            self.processes = []

    def get_mac(self):
        return self.__computer.mac

    def get_ip(self):
        return self.__computer.ip

    def __eq__(self, other):
        if isinstance(other, ClientInterface):
            return self.__computer.mac == self.__computer.mac
        elif isinstance(other, Computer):
            return self.__computer.mac == other.mac
        else:
            return False

    def update_processes(self):
        self.__send("UpdateProcesses")
        data = self.__receive()
        process_list = [item[1:-1] for item in data[1:-1].split(", ")]
        self.processes = []
        for item in process_list:
            process_parts = item.split(PROCESS_PARTS_SEPARATOR)
            try:
                process = Process(process_parts[0], process_parts[1], process_parts[2])
            except:
                pass
            else:
                self.processes.append(process)

    def __send(self, data):
        to_send = self.__encrypt(data)
        self.__socket.send(to_send)

    def __encrypt(self, data):
        result = self.__key.encrypt(data) + IN_PACK_SEPARATOR + Cipher.hash(data)
        return result

    def __receive(self):
        parts = {}
        length = self.__socket.recv(BUFFER_SIZE)
        for i in xrange(int(length)):
            data = self.__socket.recv(BUFFER_SIZE)
            number, data = data.split(FRAGMENTS_SEPARATOR)
            parts[int(number)] = data
        data = ""
        for i in xrange(int(length)):
            data += parts[i]
        return self.__decrypt(data)

    def __decrypt(self, data):
        result, hashed = data.split(IN_PACK_SEPARATOR)
        result = self.__key.decrypt(result)
        if Cipher.hash(result) == hashed:
            return result
        else:
            raise EnvironmentError("CLIENT UNAUTHORISED")

    def terminate(self, processes):
        result = ""
        for process in processes:
            if isinstance(process, Process):
                self.__send("TerminateProcess " + process.pid + " " + process.name)
                result += self.__receive()
        return result

    def open_process(self, command):
        self.__send("CreateProcess " + command)
        result = self.__receive()
        return result

    def send_files(self, directory):
        self.__send("GetFile " + directory)
        result = self.__receive()
        if "ERROR" not in result:
            result = result.split(FILE_SEPARATOR)
            return result
        return result

    def delete_file(self, path):
        self.__send("DeleteFile " + path)
        result = self.__receive()
        return result

    def create_file(self, path, name):
        self.__send("CreateFile " + path + " " + name)
        result = self.__receive()
        return result


class ClientList(object):
    def __init__(self):
        self.__items = []

    def __len__(self):
        return len(self.__items)

    def __getitem__(self, key):
        return self.__items[key]

    def __delitem__(self, key):
        del self.__items[key]

    def __setitem__(self, key, value):
        if isinstance(value, ClientInterface):
            self.__items[key] = value

    def append(self, item):
        if isinstance(item, ClientInterface):
            self.__items.append(item)

    def remove(self, item):
        if isinstance(item, ClientInterface):
            self.__items.remove(item)
        elif isinstance(item, socket):
            for client in self.__items:
                if client.socket is item:
                    self.__items.remove(client)
                    break

    def __iter__(self):
        for item in self.__items:
            yield item


class Computer(object):
    def __init__(self, mac, ip, active=True):
        self.mac = mac
        self.ip = ip
        self.active = active

    def __eq__(self, other):
        if isinstance(other, Computer):
            return self.mac == other.mac
        if isinstance(other, ClientInterface):
            return self.mac == other.get_mac()
        return False

    def __repr__(self):
        if self.active:
            status = "online"
        else:
            status = "offline"
        return self.mac + " " * 4 + self.ip + " " * 4 + status

    def __str__(self):
        if self.active:
            status = "online"
        else:
            status = "offline"
        return self.mac + " " * 4 + self.ip + " " * 4 + status

    def wake_up(self):
        if not self.active:
            wake_on_lan(self.mac)
            self.active = True
        else:
            raise NameError

    def shutdown(self):
        if self.active:
            shutdown(self.ip, "This computer will be shud down by the network manager.", 5)
            self.active = False
        else:
            raise NameError