from Constants import *
from socket import gethostbyaddr
from WakeOnLan import wake_on_lan, shutdown
from Process import Process


class ClientInterface(object):
    def __init__(self, sock, computer):
        self.__socket = sock
        if not isinstance(computer, Computer):
            raise ValueError
        else:
            self.__computer = computer
            self.name = gethostbyaddr(computer.ip)[0]
            self.processes = []
            self.update_processes()

    def get_mac(self):
        return self.__computer.mac

    def get_ip(self):
        return self.__computer.ip

    def __eq__(self, other):
        if isinstance(other, ClientInterface):
            return self.__computer.mac == self.__computer.mac
        elif isinstance(other,  Computer):
            return self.__computer.mac == other.mac
        else:
            return False

    def update_processes(self):
        self.send("UpdateProcesses")
        data = self.receive()
        data = data.replace(BROKEN_END_LINE, END_LINE)
        data = data[1:-1].split(", ")
        self.processes = []
        for item in data:
            parts = item.split(END_LINE)
            name = parts[0].split()[-1]
            pid = parts[1].split()[-1]
            parent_id = parts[2].split()[-1]
            self.processes.append(Process(name, pid, parent_id))

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
            self.__items.append(item)

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
            shutdown(self.ip)
            self.active = False
        else:
            raise NameError