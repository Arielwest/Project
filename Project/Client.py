import socket
from uuid import getnode as get_mac
from Constants import *
from threading import Thread, Lock
from wmi import WMI
from time import sleep
from ComputerObjects import Process
from win32file import CreateDirectory, DeleteFile, RemoveDirectory
from win32process import CreateProcess, STARTUPINFO, TerminateProcess
from win32api import OpenProcess
from win32api import GetLogicalDriveStrings
from win32con import PROCESS_ALL_ACCESS
import pickle
import pythoncom
from os import listdir
from os.path import exists
from ctypes import windll


class Client(object):
    def __init__(self):
        self.__socket = socket.socket()
        self.__mac = get_mac()
        self.__name = socket.gethostname()
        self.__processes = []
        self.__processes_lock = Lock()
        self.handle_functions = {
            "CreateFile": self.__create_file,
            "DeleteFile": self.__delete_file,
            "CreateProcess": self.__create_process,
            "Kill": self.__kill,
            "UpdateProcesses": self.__send_processes,
            "FilesIn": self.__files_in
        }

    def __create_file(self, path, name):
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
                result = "Success"
            except:
                result = "ERROR"
        else:
            result = "poop"
        return result

    def __delete_file(self, path):
        if exists(path):
            try:
                if len(path.split('.')) >= 2:
                    DeleteFile(path)
                else:
                    RemoveDirectory(path)
                windll.shell32.SHEmptyRecycleBinA(None, None, 1 or 2 or 4)
                result = "Success"
            except:
                result = "ERROR"
        else:
            result = "ERROR"
        return result

    def __create_process(self, exe_path):
        try:
            CreateProcess(exe_path, None, None, None, False, ?, None, None, STARTUPINFO()) # HELP
            result = "sucess"
        except:
            result = "ERROR"
        return result

    def __kill(self, pid):
        pid = int(pid)
        process_exists = True
        for process in self.__processes:
            if process.pid == pid:
                process_exists = True
                break
        if process_exists:
            try:
                handle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
                TerminateProcess(handle, '0') # HELP
                result = "Success"
            except:
                result = "Error"
        else:
            result = "poop"
        return result


    def __send_processes(self):
        result = []
        self.__update_processes()
        self.__processes_lock.acquire()
        for process in self.__processes:
            result.append(pickle.dumps(process))
        return pickle.dumps(result)

    def __files_in(self, path):
        if path == EMPTY_PATH:
            files = ' '.join(GetLogicalDriveStrings().split('\000')[:-1])
        else:
            files = ' '.join([f for f in listdir(path)])
        return files

    def __print(self, data):
        print data

    def start(self):
        self.__print("connecting")
        is_server = True
        if is_server:
            print "connected to server."
            update_thread = Thread(target=self.__update_processes_routine)
            update_thread.setDaemon(True)
            update_thread.start()
            self.__run()
        else:
            print "server not found."

    def __find_server(self):
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
        to_read, to_write, error = select([self.__socket], [self.__socket], [])
        if self.__socket in to_read:
            data = self.__socket.recv(BUFFER_SIZE)
            if data == "":
                self.__print("Lost connection with server.")
                exit()
            return data
        return ""
        """
        return raw_input("DATA: ")

    def __return_answer(self, data):
        """
        to_send = [data[i:i + BUFFER_SIZE] for i in xrange(0, len(data), BUFFER_SIZE)]
        self.__socket.send(str(len(to_send)))
        for part in to_send:
            self.__socket.send(part)
            """
        print data

    def __update_processes_routine(self):
        while True:
            pythoncom.CoInitialize()
            self.__update_processes()
            pythoncom.CoUninitialize()
            sleep(PROCESS_ENUMERATE_SLEEP)

    def __update_processes(self):
        wmi = WMI()
        self.__processes_lock.acquire()
        self.__processes = []
        for process in wmi.Win32_Process():
            process_object = Process(process.Name, process.ProcessID, process.ParentProcessID)
            self.__processes.append(process_object)
        self.__processes_lock.release()



def main():
    client = Client()
    client.start()


if __name__ == "__main__":
    main()
