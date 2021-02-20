# NE_auditor v.01
# Скрипт написан для частных задач, решаемых в конкретном проекте и не является универсальным инструментом (пока).
# Да и может он не много (пока).
import datetime
import getpass
import os
import shutil
import ipaddress
from netmiko import (Netmiko, ssh_exception)

v_date_time: str = str(datetime.date.today())
v_ip_list_file: str = 'ne_list.txt'
v_commands_file: str = 'ne_commands.txt'
v_path: str = './audit_result_' + v_date_time
v_coms = v_nes = ()  # определяем список команд и список NE

def f_checkip(v_ip):
    try:
        ipaddress.ip_address(v_ip)
    except (ipaddress.AddressValueError, ValueError) as e:
        v_ip_description: str = 'Bad format IP address!'
        return False, v_ip_description
    if ipaddress.ip_address('0.0.0.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('0.255.255.255'):
        v_ip_description = "Current network (only valid as source address)."
        return False, v_ip_description
    elif ipaddress.ip_address('100.64.0.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('100.127.255.255'):
        v_ip_description = """Shared address space for communications between a service provider and its subscribers 
        when using a carrier-grade NAT."""
        return False, v_ip_description
    elif ipaddress.ip_address('127.0.0.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('127.255.255.255'):
        v_ip_description = "Used for loopback addresses to the local host."
        return False, v_ip_description
    elif ipaddress.ip_address('169.254.0.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('169.254.255.255'):
        v_ip_description = """Used for link-local addresses between two hosts on a single link when no IP address is 
        otherwise specified, such as would have normally been retrieved from a DHCP server."""
        return False, v_ip_description
    elif ipaddress.ip_address('192.0.0.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('192.0.0.255'):
        v_ip_description = "IETF Protocol Assignments."
        return False, v_ip_description
    elif ipaddress.ip_address('192.0.2.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('192.0.2.255'):
        v_ip_description = "Assigned as TEST-NET-1, documentation and examples."
        return False, v_ip_description
    elif ipaddress.ip_address('192.88.99.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('192.88.99.0'):
        v_ip_description = "Reserved. Formerly used for IPv6 to IPv4 relay."
        return False, v_ip_description
    elif ipaddress.ip_address('198.18.0.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('198.19.255.255'):
        v_ip_description = "Used for benchmark testing of inter-network communications between two separate subnets."
        return False, v_ip_description
    elif ipaddress.ip_address('198.51.100.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('198.51.100.255'):
        v_ip_description = "Assigned as TEST-NET-2, documentation and examples."
        return False, v_ip_description
    elif ipaddress.ip_address('203.0.113.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('203.0.113.255'):
        v_ip_description = "Assigned as TEST-NET-3, documentation and examples."
        return False, v_ip_description
    elif ipaddress.ip_address('224.0.0.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('239.255.255.255'):
        v_ip_description = "In use for IP multicast. (Former Class D network)."
        return False, v_ip_description
    elif ipaddress.ip_address('240.0.0.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('255.255.255.254'):
        v_ip_description = "In use for IP multicast. (Reserved for future use. (Former Class E network)."
        return False, v_ip_description
    elif ipaddress.ip_address(v_ip) == ipaddress.ip_address('255.255.255.255'):
        v_ip_description = """Reserved for the "limited broadcast" destination address."""
        return False, v_ip_description
    v_ip_description: str = 'IP address is valid'
    return True, v_ip_description

print(f_checkip('7.40.0.1')[1])

try:
    shutil.rmtree(v_path, ignore_errors=False, onerror=None)
except OSError:
    print (f"Удалить директорию result не удалось")

try:
    os.mkdir(v_path)
except OSError:
    print (f"Создать директорию result не удалось")

try:
    with open(v_ip_list_file, 'r') as v_ipreader:
        v_readedip: str = v_ipreader.readline()
        while v_readedip:
            v_nes = v_nes + (v_readedip.rstrip(),)
            v_readedip = v_ipreader.readline()
except FileNotFoundError:
    print(f"Ошибка: файл ./{v_ip_list_file}, содержащий построчный список IP-адресов сетевых элементов, не найден.")

try:
    with open(v_commands_file, 'r') as v_commreader:
        v_line: str = v_commreader.readline()
        while v_line:
            v_coms = v_coms + (v_line.rstrip(),)
            v_line = v_commreader.readline()
except FileNotFoundError:
    print(f"Ошибка: файл ./{v_commands_file}, содержащий построчный список команд, не найден.")

v_counter: int = 1
for x in v_nes:
    try:
        os.mkdir(v_path + '\\' + f"NE-{v_counter} (" + x + ")")
    except OSError:
        print(f"Создать директорию не удалось")
    else:
        v_nedir = v_path + '\\' + f"NE-{v_counter} (" + x + ")"
        v_counter += 1
        for v_comanda in v_coms:
            v_filename: str = v_nedir + "\\" + "(" + x + ")_" + v_comanda + ".log"
            with open(v_filename, 'w') as f:
                f.write('new test')
                f.close()
print('\n\n', v_nes)
print('\n\n', v_coms)


v_login = input("Введите логин аудитора: ")
try:
    v_pass = getpass.getpass("Введите пароль аудитора: ")
except Exception as err:
    print('Ошибка: ', err)


host = {
    "host": "192.168.1.1",
    "username": "root",
    "password": "pa$$w0rd",
    "device_type": "huawei",
    "global_delay_factor": 0.1,  # Increase all sleeps by a factor of 1
}

try:
    net_connect = Netmiko(**host)
except ssh_exception.NetmikoTimeoutException:
    print('!!!!!!!!!OOOOOOOOOOOOOOOOOOO!!!!!!!!!!!!!!!')
else:
    v_command = ["display current config", "display version"]
    print("Connected to:", net_connect.find_prompt())
    output = net_connect.send_config_set(v_command, delay_factor=.5)
    net_connect.disconnect()
    print(output)
