"""
NE_auditor v.01
Скрипт написан для частных задач, решаемых в конкретном проекте и не является универсальным инструментом (пока).
Да и может он не много (пока).
"""
import datetime
import getpass
import os
import shutil
from netmiko import (Netmiko, ssh_exception)
import ff_ipchecker


v_date_time: str = str(datetime.date.today())
v_ip_list_file: str = 'ne_list.txt'
v_commands_file: str = 'ne_commands.txt'
v_path: str = './audit_result_' + v_date_time
v_coms = v_nes = ()  # определяем список команд и список NE

try:
    shutil.rmtree(v_path, ignore_errors=False, onerror=None)
except OSError:
    print (f"Удалить директорию result не удалось")

try:
    os.mkdir(v_path)
except OSError:
    print (f"Создать директорию result не удалось")

try:
    """ Считывание IP-адресов из файла в кортеж """
    with open(v_ip_list_file, 'r') as v_ipreader:
        v_readedip: str = v_ipreader.readline()
        v_counter = 1
        while v_readedip:
            v_counter += 1
            if ff_ipchecker.f_checkip(v_readedip.rstrip())[0]:
                v_nes = v_nes + (v_readedip.rstrip(),)
            else:
                print(f"Error (string {v_counter}): "
                      f"{v_readedip.rstrip()}: "
                      f"{ff_ipchecker.f_checkip(v_readedip.rstrip())[1]}")
            v_readedip = v_ipreader.readline()
        v_nes = tuple(set(v_nes))  # убираем дублирующиеся IP'шники
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


v_login = input("Введите логин: ")
try:
    v_pass = getpass.getpass("Введите пароль: ")
except Exception as err:
    print('Ошибка: ', err)

v_ne_ssh = {
    "host": "172.16.1.2",
    "username": "auditor",
    "password": "1qaz@WSX",
    "device_type": "huawei",
    # "global_delay_factor": 0.1,  # Increase all sleeps by a factor of 1
}

try:
    net_connect = Netmiko(**v_ne_ssh)
except ssh_exception.NetmikoTimeoutException:
    print(f'Не удалось подключиться к {v_ne_ssh["host"]}')
else:
    v_command = "display current-configuration"
    print("Connected to:", net_connect.find_prompt())
    output = net_connect.send_command_timing(v_command)
    net_connect.disconnect()
    print(output)
