# NE_auditor v.01
# Скрипт написан для частных задач, решаемых в конкретном проекте и не является универсальным инструментом (пока).
# Да и может он не много (пока).
import datetime
import getpass
import os
import shutil
from netmiko import (Netmiko, ssh_exception)
import ff_ipchecker

print(ff_ipchecker.f_checkip('240.40.0.1'))

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
