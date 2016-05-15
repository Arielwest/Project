# region ---------------------------- ABOUT ----------------------------
"""
##################################################################
# Created By: Ariel Westfried                                    #
# Date: 01/01/2016                                               #
# Name: Project - Process                                        #
# Version: 1.0                                                   #
# Windows Tested Versions: Win 7 32-bit                          #
# Python Tested Versions: 2.6 32-bit                             #
# Python Environment  : PyCharm                                  #
##################################################################
"""
# endregion

# region ---------------------------- IMPORTS ----------------------------
from Constants import *
# endregion

# region ---------------------------- Process CLASS ----------------------------


class Process(object):
    # constructor
    def __init__(self, name, pid, parent_id):
        self.name = name
        self.pid = pid
        self.parent_id = parent_id

    # to string
    def __str__(self):
        return "Name: " + self.name + END_LINE + "PID: " + self.pid + END_LINE + "Parent ID: " + self.pid

    # to string
    def __repr__(self):
        return "Name: " + self.name + END_LINE + "PID: " + self.pid + END_LINE + "Parent ID: " + self.pid

    # for use boolean statements
    def __eq__(self, other):
        if isinstance(other, Process):
            return self.pid == other.pid
        else:
            raise ValueError
# endregion
