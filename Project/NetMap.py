from Constants import *
import re
import subprocess
import wmi
from scapy.all import *
from ComputerObjects import *


class NetMap(object):

    @staticmethod
    def map():
        list1 = NetMap.__map_with_cmd()
        list2 = NetMap.__map_with_scapy()
        result_list = NetMap.__combine_tables(list1, list2)
        return result_list

    @staticmethod
    def __combine_tables(list1, list2):
        result_list = list(list1)
        result_list += list(list2)
        return result_list

    @staticmethod
    def __map_with_cmd():
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

    @staticmethod
    def __map_with_scapy():
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
    def __ip_and(gW, mask):
        return int(gW) & int(mask)

    @staticmethod
    def __get_network_attributes():
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


def is_ip(ip):
    return re.match(IP_REGULAR_EXPRESSION, ip)


def main():
    print "scanning...\r\nIt will take a while."
    arp_table = NetMap.map()
    print "scan complete!"
    for computer in arp_table:
        print computer.mac + " " * 4 + computer.ip + " " * 4 + computer.computer_name

if __name__ == "__main__":
    main()