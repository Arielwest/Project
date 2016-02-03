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
