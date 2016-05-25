# region ---------------------------- ABOUT ----------------------------
"""
##################################################################
# Created By: Ariel Westfried                                    #
# Date: 01/01/2016                                               #
# Name: Project - Client                                         #
# Version: 1.0                                                   #
# Windows Tested Versions: Win 7 32-bit                          #
# Python Tested Versions: 2.6 32-bit                             #
# Python Environment  : PyCharm                                  #
##################################################################
"""
# endregion

# region ---------------------------- IMPORTS ----------------------------
import socket
from uuid import getnode as get_mac
from Constants import *
from threading import Thread, Lock
from wmi import WMI
from time import sleep
from win32file import CreateDirectory, DeleteFile, RemoveDirectory
from win32process import CreateProcess, STARTUPINFO, TerminateProcess, STARTF_USESHOWWINDOW
from win32api import OpenProcess, GetLogicalDriveStrings, CloseHandle
from win32con import PROCESS_TERMINATE, NORMAL_PRIORITY_CLASS, SW_NORMAL
import pythoncom
import os
from os.path import exists
from ctypes import windll
from select import select
from Process import Process
import pickle
import subprocess
import sys
from Cipher import Cipher
# endregion

# region ---------------------------- CLASS Client ----------------------------


class Client(object):
    def __init__(self):
        self.__socket = socket.socket()
        self.__mac = get_mac()
        self.__name = socket.gethostname()
        self.__processes = []
        self.__key = Cipher.random_key()
        self.handle_functions = {
            "CreateFile": self.__create_file,
            "DeleteFile": self.__delete_file,
            "CreateProcess": self.__create_process,
            "TerminateProcess": self.__terminate_process,
            "UpdateProcesses": self.__send_processes,
            "GetFile": self.__get_file,
            "Upload": self.__send_file
        }

    def __send_file(self, directory):
        try:
            the_file = open(directory, 'rb')
            file_data = the_file.read()
            the_file.close()
            return file_data
        except:
            return "ERROR: File doesn't exists!"

    def __create_file(self, path, name):
        """
        Creates a new file in directory
        """
        if exists(path):
            directory = path
            if not directory.endswith('\\'):
                directory += '\\'
            directory += name
            try:
                if len(directory.split('.')) >= 2:
                    open(directory, 'w')
                else:
                    CreateDirectory(directory, None)
                result = "Created " + directory
            except:
                result = "ERROR: internal error"
        else:
            result = "ERROR: no directory " + path
        return result

    def __delete_file(self, path):
        """
        Deltes the file in path
        """
        if exists(path):
            try:
                if len(path.split('.')) >= 2:
                    DeleteFile(path)
                else:
                    RemoveDirectory(path)
                windll.shell32.SHEmptyRecycleBinA(None, None, 1 or 2 or 4)
                result = "Deleted " + path
            except:
                result = "ERROR: internal error"
        else:
            result = "ERROR: no directory " + path
        return result

    def __create_process(self, command):
        """
        Opens a new process
        """
        try:
            startup_info = STARTUPINFO()
            startup_info.dwFlags = STARTF_USESHOWWINDOW
            startup_info.wShowWindow = SW_NORMAL
            CreateProcess(None, command, None, None, 0, NORMAL_PRIORITY_CLASS, None, None, startup_info)
            result = "Opened " + command
        except:
            result = "ERROR: internal error"
        return result

    def __terminate_process(self, pid, name):
        """
        kill a process
        """
        process_exists = False
        for process in self.__processes:
            if process.pid == pid:
                process_exists = True
                break
        if process_exists:
            try:
                handle = OpenProcess(PROCESS_TERMINATE, False, int(pid))
                TerminateProcess(handle, -1)
                CloseHandle(handle)
                result = name+ '-' + pid + " terminated"
            except:
                result = "ERROR: internal error"
        else:
            result = "ERROR: no process " + name + '-' + pid
        return result

    def __send_processes(self):
        """
        Creates a list of all processes
        """
        result = []
        self.__update_processes()
        for process in self.__processes:
            process_parts = str(process.name) + PROCESS_PARTS_SEPARATOR + str(process.pid) + PROCESS_PARTS_SEPARATOR + str(process.parent_id)
            result.append(str(process_parts))
        return str(result)

    def __print(self, data):
        print data

    def start(self):
        """
        starts the client program
        """
        self.__print("connecting")
        is_server = self.__find_server()
        if is_server:
            print "connected to server."
            self.__run()
        else:
            print "server not found."

    def __find_server(self):
        """
        Looking for server in the network. if found returns True else False
        """
        search_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        search_socket.settimeout(ANNOUNCE_SLEEP_TIME)
        search_socket.bind(("0.0.0.0", BROADCAST_PORT))
        try:
            message, address = search_socket.recvfrom(BUFFER_SIZE)
        except:
            return False
        else:
            server_address = address[0]
            if message == SERVER_ANNOUNCE_MESSAGE:
                status = self.__socket.connect_ex((server_address, SERVER_PORT))
                if status == 0:
                    return self.__key_exchange()
            return False

    def __key_exchange(self):
        server_public_key_data = self.__socket.recv(BUFFER_SIZE)
        server_public_key = Cipher.unpack(server_public_key_data)
        to_send = self.__key.pack() + IN_PACK_SEPARATOR + Cipher.hash(self.__key.pack())
        to_send = server_public_key.encrypt(to_send)
        self.__socket.send(to_send)
        return True

    def __run(self):
        """
        The actual main code of the client
        """
        while True:
            data = self.__get_data()
            if data != "":
                data = data.split()
                case = len(data)
                try:
                    if case == 3:
                        result = self.handle_functions[data[0]](data[1], data[2])
                    elif case == 2:
                        result = self.handle_functions[data[0]](data[1])
                    elif case == 1:
                        result = self.handle_functions[data[0]]()
                    else:
                        result = "ERROR"
                except:
                    result = "ERROR"
                self.__return_answer(result)

    def __get_data(self):
        """
        Relieves the requests from the server
        """
        to_read, to_write, error = select([self.__socket], [self.__socket], [])
        if self.__socket in to_read:
            try:
                data = self.__socket.recv(BUFFER_SIZE)
            except socket.error:
                data = ""
            if data == "":
                self.__print("Lost connection with server.")
                exit()
            return self.__decrypt(data)
        return ""

    def __encrypt(self, data):
        result = self.__key.encrypt(data) + IN_PACK_SEPARATOR + Cipher.hash(data)
        return result

    def __decrypt(self, data):
        data, hashed = data.split(IN_PACK_SEPARATOR)
        data = self.__key.decrypt(data)
        if Cipher.hash(data) == hashed:
            return data
        else:
            raise EnvironmentError("Server Unauthorised")

    def __return_answer(self, data):
        """
        sends back the result
        """
        to_send = self.__encrypt(data)
        num_size = len(to_send) / BUFFER_SIZE + 1
        if str(len(to_send)).startswith('9'):
            num_size += 1
        to_send = [to_send[i:i + BUFFER_SIZE - (num_size + 1)] for i in xrange(0, len(to_send), BUFFER_SIZE - (num_size + 1))]
        self.__socket.send(str(len(to_send)))
        sleep(1)
        for i in xrange(len(to_send)):
            num = str(i)
            num = "".join([str(j - j) for j in xrange(num_size - len(num))]) + num
            self.__socket.send(num + "@" + to_send[i])

    def __update_processes(self):
        """
        Enumerates all running processes
        """
        wmi = WMI()
        self.__processes = []
        for process in wmi.Win32_Process():
            process_object = Process(process.Name, str(process.ProcessID), str(process.ParentProcessID))
            self.__processes.append(process_object)

    def __get_file(self, path):
        """
        Returns whats is inside that file
        """
        if path == EMPTY_PATH:
            files = FILE_SEPARATOR.join(GetLogicalDriveStrings().split('\000')[:-1])
        elif exists(path):
            files = FILE_SEPARATOR.join([str(f) for f in os.listdir(path)])
        else:
            files = "ERROR: no directory " + path
        return files
# endregion

# region ---------------------------- MAIN ----------------------------


def main():
    client = Client()
    client.start()


if __name__ == "__main__":
    main()
# endregion
