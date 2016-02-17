from Constants import *
from socket import *
from struct import pack
from win32api import GetCurrentProcess, InitiateSystemShutdown
from win32con import SE_SHUTDOWN_NAME, SE_REMOTE_SHUTDOWN_NAME, SE_PRIVILEGE_ENABLED, TOKEN_ALL_ACCESS
from win32security import LookupPrivilegeValue, OpenProcessToken, AdjustTokenPrivileges


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
        send_data = ''.join([send_data, pack('B', int(data[i: i + 2], 16))])

    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    sock.sendto(send_data, ('<broadcast>', WAKE_ON_LAN_PORT))

def shutdown(host=None, msg=None, timeout=0, force=1, reboot=0):
    """
    Shutdown a computer
    """
    print host
    host = gethostbyaddr(host)[0]
    privilege1 = LookupPrivilegeValue(host, SE_SHUTDOWN_NAME)
    privilege2 = LookupPrivilegeValue(host, SE_REMOTE_SHUTDOWN_NAME)
    new_state = [(privilege1, SE_PRIVILEGE_ENABLED), (privilege2, SE_PRIVILEGE_ENABLED)]
    token = OpenProcessToken(GetCurrentProcess(), TOKEN_ALL_ACCESS)
    AdjustTokenPrivileges(token, False, new_state)
    InitiateSystemShutdown(host, msg, timeout, force, reboot)

'''
def main():
    wake_on_lan("10-60-4B-6B-6C-CF")
    # shutdown("34V7-07", "This computer will be shut down by the network manager", 5)

if __name__ == "__main__":
    main()
'''