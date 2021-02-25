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
import argparse
from netmiko import Netmiko
from netmiko import ssh_exception
from tqdm import tqdm
from ip_list_checker import f_ip_list_checker


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
        v_out_msg = f'Не удалось подключиться к NE c IP-адресом {v_ne_ssh["host"]}. Хост недоступен.'
        return v_out_msg
    except ssh_exception.NetmikoAuthenticationException:
        v_out_msg = f'Не удалось подключиться к NE c IP-адресом {v_ne_ssh["host"]}. Ошибка аутентификации.'
        return v_out_msg
    else:
        print()
        try:
            os.mkdir(v_path + '\\' + f"NE-{v_counter} (" + x + ")")
        except OSError:
            print(f"Создать директорию не удалось")
        else:
            pass
        for i in enumerate(v_comsi):
            v_filename: str = f"{v_nediri}" + r"\(" + f"{v_ne_ssh['host']})_{i[1]}.log"
            with open(v_filename, 'w') as f_output:
                output = net_connect.send_command_timing(i[1])
                f_output.write(output)
                f_output.close()
                v_out_msg = f"Успешное подключение к: {net_connect.find_prompt()}. SSH"
        net_connect.disconnect()
        return v_out_msg


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
v_nes = f_ip_list_checker(v_ip_list_file)   # определяем список NE


try:
    shutil.rmtree(v_path, ignore_errors=False, onerror=None)
except OSError:
    print("Удалить директорию result не удалось")

try:
    os.mkdir(v_path)
except OSError:
    print("Создать директорию result не удалось")

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
    print('='*15)
except Exception as err:
    print('Ошибка: ', err)

v_counter: int = 1
with tqdm(total=len(v_nes)) as pbar:
    for x in v_nes:
        pbar.set_description_str(f"NE-{v_counter}".center(7))
        v_nedir = v_path + '\\' + f"NE-{v_counter} (" + x + ")"
        v_access_via = f_ne_access(v_nes[v_counter-1], v_login, v_pass, "huawei", v_coms, v_nedir)
        v_counter += 1
        pbar.update(1)
        pbar.write(v_access_via)
print('\n\n', v_nes)
print('\n', v_coms, '\n')

input('Готово. Для завершения программы нажмите Enter.')
