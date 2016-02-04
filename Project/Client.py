import socket
from uuid import getnode as get_mac
from Constants import *
from threading import Thread, Lock
from win32com.client import GetObject
from time import sleep
from Computers import Process


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

    def __create_file(self, name, path):
        pass

    def __delete_file(self, path):
        pass

    def __create_process(self, exe_path):
        pass

    def __kill(self, pid):
        pass

    def __send_processes(self):
        pass

    def __files_in(self, path):
        pass

    def __print(self, data):
        print data

    def start(self):
        self.__print("connecting")
        is_server = self.__find_server()
        if is_server:
            print "connected to server."
            update_thread = Thread(target=self.__update_data)
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
                if case == 3:
                    result = self.handle_functions[data[0]](data[1], data[2])
                elif case == 2:
                    result = self.handle_functions[data[0]](data[1])
                elif case == 1:
                    result = self.handle_functions[data[0]]()
                else:
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
        return raw_input()

    def __return_answer(self, data):
        """
        to_send = [data[i:i + BUFFER_SIZE] for i in xrange(0, len(data), BUFFER_SIZE)]
        self.__socket.send(str(len(to_send)))
        for part in to_send:
            self.__socket.send(part)
            """
        print data

    def __update_data(self):
        wmi = GetObject(WMI_OBJECT)
        while True:
            for process in wmi.InstancesOf(PROCESS):
                process_object = Process(process.Name, process.Properties_('ProcessId'))
                children = wmi.ExecQuery('Select * from win32_process where ParentProcessId=%s' % process.Properties_('ProcessId'))
                for child in children:
                    child_object = Process(child.Name, child.Properties_('ProcessId'))
                    process_object.add_child(child_object)
                answer = False
                self.__processes_lock.acquire()
                for known_process in self.__processes:
                    answer = known_process.is_child_exist(process_object.pid)
                    if isinstance(answer, Process):
                        answer.update_self(process_object)
                        answer = True
                        break
                if not answer:
                    self.__processes.append(process_object)
                self.__processes_lock.release()
            sleep(PROCESS_ENUMERATE_SLEEP)

def main():
    client = Client()
    client.start()


if __name__ == "__main__":
    main()
