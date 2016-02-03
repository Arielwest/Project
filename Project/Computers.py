class Computer(object):
    def __init__(self, mac, ip, computer_name=""):
        self.mac = mac
        self.ip = ip
        self.computer_name = computer_name

    def __eq__(self, other):
        if isinstance(other, Computer):
            return self.mac == other.mac
        else:
            return False

    def __repr__(self):
        return self.mac + " " * 4 + self.ip + " " * 4 + self.computer_name

    def __str__(self):
        return self.mac + " " * 4 + self.ip + " " * 4 + self.computer_name


class ComputerList():
    def __init__(self):
        self.__items = []

    def append(self, new):
        if isinstance(new, Computer):
            self.__items.append(new)
        else:
            raise ValueError("ComputerList can contain only instances of Computer")

    def __delitem__(self, key):
        del self.__items[key]

    def remove(self, item):
        for computer in self.__items:
            if item is computer:
                self.__items.remove(computer)

    def __getitem__(self, index):
        return self.__items[index]

    def duplicate(self):
        result = ComputerList()
        result.__items = list(self.__items)
        return result

    def __add__(self, other):
        if isinstance(other, ComputerList):
            result = ComputerList()
            result.__items = list(self.__items)
            result.__items += other.__items
            return result
        elif isinstance(other, Computer):
            result = ComputerList()
            result.__items = list(self.__items)
            result.__items += other
            return result
        else:
            raise ValueError

    def __iadd__(self, other):
        if isinstance(other, ComputerList):
            self.__items += other.__items
        elif isinstance(other, Computer):
            self.__items += other
        else:
            raise ValueError

    def __iter__(self):
        return self.__items
