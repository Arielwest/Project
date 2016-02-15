from Constants import *
import socket
import struct
import win32api
import win32con
import win32security


def wake_on_lan(mac_address):
    """
    Wakes a computer
    """
    if len(mac_address) == MAC_LENGTH + 5:
        separator = mac_address[2]
        mac_address = mac_address.replace(separator, '')
    elif len(mac_address) != MAC_LENGTH:
        raise ValueError("Incorrect MAC address format.")

    data = ''.join(['FFFFFFFFFFFF', mac_address * 16])
    send_data = ''
    for i in range(0, len(data), 2):
        send_data = ''.join([send_data, struct.pack('B', int(data[i: i + 2], 16))])

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(send_data, ('<broadcast>', WAKE_ON_LAN_PORT))
    print send_data

def shutdown(host=None, msg=None, timeout=0, force=1, reboot=0):
    """
    Shutdown a computer
    """
    privilege1 = win32security.LookupPrivilegeValue(host, win32con.SE_SHUTDOWN_NAME)
    privilege2 = win32security.LookupPrivilegeValue(host, win32con.SE_REMOTE_SHUTDOWN_NAME)
    new_state = [(privilege1, win32con.SE_PRIVILEGE_ENABLED), (privilege2, win32con.SE_PRIVILEGE_ENABLED)]
    token = win32security.OpenProcessToken(win32api.GetCurrentProcess(), win32con.TOKEN_ALL_ACCESS)
    win32security.AdjustTokenPrivileges(token, False, new_state)
    win32api.InitiateSystemShutdown(host, msg, timeout, force, reboot)


def main():
    wake_on_lan("10-60-4B-6B-6C-CF")
    # shutdown("34V7-07", "This computer will be shut down by the network manager", 5)

if __name__ == "__main__":
    main()
