from Constants import *


class Process(object):
    def __init__(self, name, pid, parent_id):
        self.name = name
        self.pid = pid
        self.parent_id = parent_id

    def __str__(self):
        return "Name: " + self.name + END_LINE + "PID: " + self.pid + END_LINE + "Parent ID: " + self.pid

    def __repr__(self):
        return "Name: " + self.name + END_LINE + "PID: " + self.pid + END_LINE + "Parent ID: " + self.pid
