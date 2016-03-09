from Constants import *
from socket import gethostbyaddr
from WakeOnLan import wake_on_lan, shutdown
from Process import Process
from socket import socket
import pickle


class ClientInterface(object):
    def __init__(self, sock, computer):
        self.__socket = sock
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
        self.send("UpdateProcesses")
        data = self.receive()
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

    def send(self, data):
        self.__socket.send(data)

    def receive(self):
        parts = {}
        length = self.__socket.recv(BUFFER_SIZE)
        for i in xrange(int(length)):
            data = self.__socket.recv(BUFFER_SIZE)
            data = data.split('@')
            parts[int(data[0])] = '@'.join(data[1:])
        data = ""
        for i in xrange(int(length)):
            data += parts[i]
        return data

    def terminate(self, process):
        if isinstance(process, Process):
            self.send("TerminateProcess " + process.pid)
            result = self.receive()
            return result

    def open_process(self, command):
        self.send("CreateProcess " + command)
        result = self.receive()
        return result

    def send_files(self):
        self.send("UpdateFiles")
        result = self.receive()
        if "ERROR" not in result:
            result = pickle.loads(result)
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