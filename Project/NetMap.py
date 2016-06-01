# region ---------------------------- ABOUT ----------------------------
"""
##################################################################
# Created By: Ariel Westfried                                    #
# Date: 01/01/2016                                               #
# Name: Project - NetMap                                         #
# Version: 1.0                                                   #
# Windows Tested Versions: Win 7 32-bit                          #
# Python Tested Versions: 2.6 32-bit                             #
# Python Environment  : PyCharm                                  #
##################################################################
"""
# endregion

# region ---------------------------- IMPORTS ----------------------------
from Constants import *
import re
import subprocess
import wmi
# from scapy.all import *
from ClientInterface import Computer
import struct
from socket import inet_aton
# endregion

# region ---------------------------- NemMap CLASS ----------------------------


class NetMap(object):
    # main mapping method
    @staticmethod
    def map():
        """
        Main mapping function
        """
        list1 = NetMap.__map_with_cmd()
        # list2 = NetMap.__map_with_scapy()
        list2 = []
        result_list = NetMap.__combine_tables(list1, list2)
        return result_list

    # combines the two arp tables generated
    @staticmethod
    def __combine_tables(list1, list2):
        """
        Combines two lists
        """
        result_list = list(list1)
        for computer in list2:
            if computer not in result_list:
                result_list.append(computer)
        return result_list

    # takes the computer's table
    @staticmethod
    def __map_with_cmd():
        """
        Returns the computer's arp table
        """
        result = []
        pipe = subprocess.Popen(['arp', '-a'], stdout=subprocess.PIPE)
        for line in pipe.stdout.readlines()[3:]:
            try:
                ip, mac, address_type = line.split()
            except ValueError:
                ip, mac, address_type = None, None, None
            if address_type == 'dynamic':
                mac = mac.replace('-', ':')
                computer = Computer(mac, ip)
                result.append(computer)
        return result
    '''
    # surveying the netwotk with scapy
    @staticmethod
    def __map_with_scapy():
        """
        makes its own arp table
        """
        result = []
        conf.verb = 0
        my_ip, gateway_ip, my_mac, subnet_mask = NetMap.__get_network_attributes()
        # print my_ip, gateway_ip, my_mac, subnet_mask
        final_gateway = NetMap.__get_final_gateway(gateway_ip, subnet_mask)
        pkt = Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=final_gateway)
        answered, unanswered = srp(pkt, timeout=10)
        for snd, rcv in answered:
            mac = rcv.sprintf("%Ether.src%")
            ip = rcv.sprintf("%ARP.psrc%")
            computer = Computer(mac, ip)
            result.append(computer)
        return result
        '''
    # return the Broadcast address for the current network
    @staticmethod
    def __get_final_gateway(gateway_ip, subnet_mask):
        gate_array = gateway_ip.split(".", 4)
        mask_array = subnet_mask.split(".", 4)
        add_bits = NetMap.__exponent_two(mask_array[0]) + NetMap.__exponent_two(mask_array[1])\
                   + NetMap.__exponent_two(mask_array[2]) + NetMap.__exponent_two(mask_array[3])
        final_gateway = str(NetMap.__ip_and(gate_array[0], mask_array[0])) + "."
        final_gateway += str(NetMap.__ip_and(gate_array[1], mask_array[1])) + "."
        final_gateway += str(NetMap.__ip_and(gate_array[2], mask_array[2])) + "."
        final_gateway += str(NetMap.__ip_and(gate_array[3], mask_array[3]))
        final_gateway += "/" + str(add_bits)
        return final_gateway

    @staticmethod
    def __exponent_two(num):
        num = int(num)
        times = 0
        while num > 0:
            if num % 2 != 0:
                times += 1
            num /= 2
        return times

    @staticmethod
    def __ip_and(ip1, ip2):
        return int(ip1) & int(ip2)

    # gets the network attributes
    @staticmethod
    def __get_network_attributes():
        """
        returns the computer's network attributes
        """
        wmi_obj = wmi.WMI()
        sql = "select MACAddress, IPAddress, DefaultIPGateway, IPSubnet from Win32_NetworkAdapterConfiguration where IPEnabled=TRUE"
        wmi_out = wmi_obj.query(sql)
        index = 0
        for result in wmi_out:
            if is_ip(result.IPAddress[0]):
                index = wmi_out.index(result)
        my_ip, gateway_ip, my_mac = wmi_out[index].IPAddress[0], wmi_out[index].DefaultIPGateway[0], wmi_out[index].MACAddress
        subnet_mask = wmi_out[index].IPSubnet[0]
        return my_ip, gateway_ip, my_mac, subnet_mask

    @staticmethod
    def can_ip_in_my_network(ip):
        my_ip, gateway_ip, my_mac, subnet_mask = NetMap.__get_network_attributes()
        mask_array = subnet_mask.split(".", 4)
        ip_array = ip.split('.', 4)
        gateway_array = gateway_ip.split('.', 4)
        net_address1 = str(NetMap.__ip_and(gateway_array[0], mask_array[0])) + "."
        net_address1 += str(NetMap.__ip_and(gateway_array[1], mask_array[1])) + "."
        net_address1 += str(NetMap.__ip_and(gateway_array[2], mask_array[2])) + "."
        net_address1 += str(NetMap.__ip_and(gateway_array[3], mask_array[3]))
        net_address2 = str(NetMap.__ip_and(ip_array[0], mask_array[0])) + "."
        net_address2 += str(NetMap.__ip_and(ip_array[1], mask_array[1])) + "."
        net_address2 += str(NetMap.__ip_and(ip_array[2], mask_array[2])) + "."
        net_address2 += str(NetMap.__ip_and(ip_array[3], mask_array[3]))
        if net_address1 == net_address2:
            return True
        return False

# endregion


# checks if ip is valid
def is_ip(ip):
    return re.match(IP_REGULAR_EXPRESSION, ip)

# region ---------------------------- MAIN ----------------------------


# Prints an up to date arp table
def main():
    '''
    print "scanning...\r\nIt will take a while."
    arp_table = NetMap.map()
    print "scan complete!"
    for computer in arp_table:
        print computer.mac + " " * 4 + computer.ip + " " * 4 + computer.computer_name
        '''
    print NetMap.can_ip_in_my_network("192.168.100.55")
    print NetMap.can_ip_in_my_network("200.69.3.55")

if __name__ == "__main__":
    main()
# endregion
