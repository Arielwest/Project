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
    def __init__(self, name, pid, children=None):
        self.name = name
        self.pid = pid
        self.children = []
        if isinstance(children, list):
            for item in children:
                if isinstance(item, Process):
                    self.children.append(item)

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

    def update_self(self, process):
        if isinstance(process, Process) and self.pid == process.pid:
            self.name = process.name
            self.children = process.children
        else:
            raise ValueError
