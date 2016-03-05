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
from os import listdir
from os.path import exists
from ctypes import windll
from select import select
from Process import Process
import pickle


class Client(object):
    def __init__(self):
        self.__socket = socket.socket()
        self.__mac = get_mac()
        self.__name = socket.gethostname()
        self.__processes = []
        self.__processes_lock = Lock()
        self.__update_processes()
        self.handle_functions = {
            "CreateFile": self.__create_file,
            "DeleteFile": self.__delete_file,
            "CreateProcess": self.__create_process,
            "TerminateProcess": self.__terminate_process,
            "UpdateProcesses": self.__send_processes,
            "FilesIn": self.__files_in
        }

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

    def __terminate_process(self, pid):
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
                handle = OpenProcess(PROCESS_TERMINATE, False, pid)
                TerminateProcess(handle, -1)
                CloseHandle(handle)
                result = pid + " terminated"
            except:
                result = "ERROR: internal error"
        else:
            result = "ERROR: no process " + str(pid)
        return result

    def __send_processes(self):
        """
        Creates a list of all processes
        """
        result = []
        self.__update_processes()
        self.__processes_lock.acquire()
        for process in self.__processes:
            process_parts = str(process.name) + "+" + str(process.pid) + "+" + str(process.parent_id)
            result.append(str(process_parts))
        self.__processes_lock.release()
        return str(result)

    def __files_in(self, path):
        """
        Returns whats is inside that file
        """
        if path == EMPTY_PATH:
            files = ' '.join(GetLogicalDriveStrings().split('\000')[:-1])
        elif exists(path):
            files = ' '.join([f for f in listdir(path)])
        else:
            files = "ERROR: no directory " + path
        return files

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
            update_thread = Thread(target=self.__update_processes_routine)
            update_thread.setDaemon(True)
            update_thread.start()
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
                    return True
            return False

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
            return data
        return ""

    def __return_answer(self, data):
        """
        sends back the result
        """
        to_send = [data[i:i + BUFFER_SIZE - 4] for i in xrange(0, len(data), BUFFER_SIZE)]
        self.__socket.send(str(len(to_send)))
        for i in xrange(len(to_send)):
            num = str(i)
            num = "".join([str(j - j) for j in xrange(3 - len(num))]) + num
            self.__socket.send(num + "@" + to_send[i])

    def __update_processes_routine(self):
        """
        This is run in a thread, activates update_processes any PROCESS_ENUMERATE_SLEEP seconds
        """
        while True:
            pythoncom.CoInitialize()
            self.__update_processes()
            pythoncom.CoUninitialize()
            sleep(PROCESS_ENUMERATE_SLEEP)

    def __update_processes(self):
        """
        Enumerates all running processes
        """
        wmi = WMI()
        self.__processes_lock.acquire()
        self.__processes = []
        for process in wmi.Win32_Process():
            process_object = Process(process.Name, str(process.ProcessID), str(process.ParentProcessID))
            self.__processes.append(process_object)
        self.__processes_lock.release()


def main():
    client = Client()
    client.start()


if __name__ == "__main__":
    main()
