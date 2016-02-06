class Computer(object):
    def __init__(self, mac, ip, active=True):
        self.mac = mac
        self.ip = ip
        self.active = active

    def __eq__(self, other):
        if isinstance(other, Computer):
            return self.mac == other.mac
        else:
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


class Process(object):
    def __init__(self, name, pid, parent_id):
        self.name = name
        self.pid = pid
        self.parent_id = parent_id

    """
    def add_child(self, process):
        if isinstance(process, Process):
            self.children.append(process)
        else:
            raise ValueError

    def is_child_exist(self, pid):
        if self.pid == pid:
            return self
        else:
            for child in self.children:
                answer = child.is_child_exist(pid)
                if not answer == False:
                    return answer
        return False

    def make_list(self):
        return_list = [self]
        for process in self.children:
            return_list += process.make_list()
        return return_list


class ProcessParentsList(object):
    def __init__(self):
        self.__items = []

    def __len__(self):
        return len(self.__items)

    def __getitem__(self, key):
        return self.__items[key]

    def __delitem__(self, key):
        del self.__items[key]

    def __setitem__(self, key, value):
        if isinstance(value, Process):
            self.__items[key] = value

    def append(self, item):
        if isinstance(item, Process):
            self.__items.append(item)

    def __iter__(self):
        for item in self.__items:
            yield item

    def make_list(self):
        return_list = []
        for process in self.__items:
            return_list += process.make_list()
        return return_list
"""
