# coding: utf-8

"""
NE_auditor v.01
Скрипт написан для частных задач, решаемых в конкретном проекте и не является универсальным инструментом (пока).
Да и может он не много (пока).
"""


import datetime
import getpass
import os
import shutil
from netmiko import Netmiko
from netmiko import ssh_exception
import ipaddress
import argparse


def f_checkip(v_ip):
    """
    Проверка валидности IP-адреса для назначения на интерфейсе. Скорипт проверяепт как формат, так и принадлежность
    зарезервированным пулам адресов, которые не могут использоваться с этой целью.
    """
    try:
        ipaddress.ip_address(v_ip)
    except (ipaddress.AddressValueError, ValueError):
        v_ip_description: str = 'Invalid IP-address format.'
        return False, v_ip_description
    if ipaddress.ip_address('0.0.0.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('0.255.255.255'):
        v_ip_description = "Bad IP: Current network (only valid as source address)."
        return False, v_ip_description
    elif ipaddress.ip_address('100.64.0.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('100.127.255.255'):
        v_ip_description = """Bad IP: Shared address space for communications between a service provider and its 
        subscribers when using a carrier-grade NAT."""
        return False, v_ip_description
    elif ipaddress.ip_address('127.0.0.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('127.255.255.255'):
        v_ip_description = "Bad IP: Used for loopback addresses to the local host."
        return False, v_ip_description
    elif ipaddress.ip_address('169.254.0.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('169.254.255.255'):
        v_ip_description = """Bad IP: Used for link-local addresses between two hosts on a single link when no IP 
        address is otherwise specified, such as would have normally been retrieved from a DHCP server."""
        return False, v_ip_description
    elif ipaddress.ip_address('192.0.0.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('192.0.0.255'):
        v_ip_description = "Bad IP: IETF Protocol Assignments."
        return False, v_ip_description
    elif ipaddress.ip_address('192.0.2.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('192.0.2.255'):
        v_ip_description = "Bad IP: Assigned as TEST-NET-1, documentation and examples."
        return False, v_ip_description
    elif ipaddress.ip_address('192.31.196.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('192.31.196.255'):
        v_ip_description = "Bad IP: AS112-v4."
        return False, v_ip_description
    elif ipaddress.ip_address('192.52.193.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('192.52.193.255'):
        v_ip_description = "Bad IP: AMT."
        return False, v_ip_description
    elif ipaddress.ip_address('192.88.99.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('192.88.99.0'):
        v_ip_description = "Bad IP: Reserved. Formerly used for IPv6 to IPv4 relay."
        return False, v_ip_description
    elif ipaddress.ip_address('192.175.48.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('192.175.48.0'):
        v_ip_description = "Bad IP: Direct Delegation AS112 Service."
        return False, v_ip_description
    elif ipaddress.ip_address('198.18.0.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('198.19.255.255'):
        v_ip_description = """Bad IP: Used for benchmark testing of inter-network communications
        between two separate subnets."""
        return False, v_ip_description
    elif ipaddress.ip_address('198.51.100.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('198.51.100.255'):
        v_ip_description = "Bad IP: Assigned as TEST-NET-2, documentation and examples."
        return False, v_ip_description
    elif ipaddress.ip_address('203.0.113.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('203.0.113.255'):
        v_ip_description = "Bad IP: Assigned as TEST-NET-3, documentation and examples."
        return False, v_ip_description
    elif ipaddress.ip_address('224.0.0.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('239.255.255.255'):
        v_ip_description = "Bad IP: In use for IP multicast. (Former Class D network)."
        return False, v_ip_description
    elif ipaddress.ip_address('240.0.0.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('255.255.255.254'):
        v_ip_description = "Bad IP: In use for IP multicast. Reserved for future use. (Former Class E network)."
        return False, v_ip_description
    elif ipaddress.ip_address(v_ip) == ipaddress.ip_address('255.255.255.255'):
        v_ip_description = """Bad IP: Reserved for the "limited broadcast" destination address."""
        return False, v_ip_description
    v_ip_description: str = 'IP address is valid'
    return True, v_ip_description


def f_ne_access(v_host_ip, v_username, v_password, v_vendor, v_comsi, v_nediri):
    """     вывод команд в файл    """
    v_ne_ssh = {
        "host": v_host_ip,
        "username": v_username,
        "password": v_password,
        "device_type": v_vendor,
        # "global_delay_factor": 0.1,  # Increase all sleeps by a factor of 1
    }

    try:
        net_connect = Netmiko(**v_ne_ssh)
    except ssh_exception.NetmikoTimeoutException:
        print(f'Не удалось подключиться к NE c IP-адресом {v_ne_ssh["host"]}')
        return 'Не доступен'
    else:
        print("Успешное подключение к:", net_connect.find_prompt())
        for i in enumerate(v_comsi):
            v_filename: str = f"{v_nediri}" + r"\(" + f"{v_ne_ssh['host']})_{i[1]}.log"
            with open(v_filename, 'w') as f_output:
                output = net_connect.send_command_timing(i[1])
                f_output.write(output)
                f_output.close()
        net_connect.disconnect()
        return 'SSH'


parser = argparse.ArgumentParser()
parser.add_argument("-n", "--network-elements-list", action="store", dest="n",
                    help="Файл со списком сетевых элементов (NE)", default="ne_list.txt")
parser.add_argument("-c", "--command-list", action="store", dest="c",
                    help="Файл со списком консольных команд для сетевых элементов (NE)", default="ne_commands.txt")
args = parser.parse_args()
v_ip_list_file: str = args.n
v_commands_file: str = args.c

v_date_time: str = str(datetime.date.today())
v_path: str = './audit_result_' + v_date_time
v_coms = ()  # определяем список команд
v_nes = ()   # определяем список NE

try:
    shutil.rmtree(v_path, ignore_errors=False, onerror=None)
except OSError:
    print("Удалить директорию result не удалось")

try:
    os.mkdir(v_path)
except OSError:
    print("Создать директорию result не удалось")

try:
    """ Считывание IP-адресов из файла в кортеж """
    with open(v_ip_list_file, 'r') as v_ipreader:
        v_readedip: str = v_ipreader.readline()
        v_counter = 1
        while v_readedip:
            v_counter += 1
            if f_checkip(v_readedip.rstrip())[0]:
                v_nes = v_nes + (v_readedip.rstrip(),)
            else:
                print(f"Ошибка в строке [{v_counter}] "
                      f"{v_readedip.rstrip()}: "
                      f"{f_checkip(v_readedip.rstrip())[1]}")
            v_readedip = v_ipreader.readline()
        v_nes = sorted(tuple(set(v_nes)))  # сортируем и убираем дублирующиеся IP'шники
except FileNotFoundError:
    print(f"Ошибка: файл ./{v_ip_list_file}, "
          f"содержащий построчный список IP-адресов сетевых элементов, не найден.")

try:
    """ Считывание списка команд из файла в кортеж """
    with open(v_commands_file, 'r') as v_commreader:
        v_line: str = v_commreader.readline()
        while v_line:
            v_coms = v_coms + (v_line.rstrip(),)
            v_line = v_commreader.readline()
        v_coms = tuple(set(v_coms))  # убираем дублирующиеся команды
except FileNotFoundError:
    print(f"Ошибка: файл ./{v_commands_file}, содержащий построчный список команд, не найден.")

v_login = input("Введите логин (общий на все NE): ")
v_pass: str = ''
try:
    v_pass = getpass.getpass("Введите пароль: ")
except Exception as err:
    print('Ошибка: ', err)

v_counter: int = 1
v_access_via: str = ''
for x in v_nes:
    try:
        os.mkdir(v_path + '\\' + f"NE-{v_counter} (" + x + ")")
    except OSError:
        print(f"Создать директорию не удалось")
    else:
        v_nedir = v_path + '\\' + f"NE-{v_counter} (" + x + ")"
        v_access_via = f_ne_access(v_nes[v_counter-1], v_login, v_pass, "huawei", v_coms, v_nedir)
        v_counter += 1
        print(v_access_via)
print('\n\n', v_nes)
print('\n', v_coms, '\n')

input('Готово. Для завершения программы нажмите Enter.')
