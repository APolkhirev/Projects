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
import pandas  # для табличного отчёта
import tqdm
from netmiko import Netmiko
from netmiko import ssh_exception
from ip_list_checker import f_ip_list_checker


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
v_keys = ['hostname', 'ip', 'model', 'version', 'patch', 'status']
v_ne_status = dict.fromkeys(v_keys)
v_report = []
dd_com_sw = "Software Version"
dd_com_pw = "Patch Package Version:"
dd_com_dw = "display device"


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
    print('='*15, 'СТАРТ','='*15)
except Exception as err:
    print('Ошибка: ', err)

v_counter: int = 1
with tqdm.tqdm(total=len(v_nes), desc="Обработано NE") as pbar:
    for v_ne_ip in v_nes:
        v_ne = f"NE-{v_counter}"
        v_nedir = v_path + '\\' + f"{v_ne} (" + v_ne_ip + ")"
        v_out_msg = ''
        v_ne_ssh = {
            "host": v_ne_ip,
            "username": v_login,
            "password": v_pass,
            "device_type": 'huawei',
            "global_delay_factor": 0.1,  # Increase all sleeps by a factor of 1
        }
        v_report.append(v_ne_status.copy())
        v_report[v_counter-1]['ip'] = v_ne_ip

        try:
            net_connect = Netmiko(**v_ne_ssh)
        except ssh_exception.NetmikoTimeoutException:
            pbar.write(f'Не удалось подключиться к NE c IP-адресом {v_ne_ip}. Хост недоступен.')
            v_report[v_counter-1]['status'] = f'No access'
        except ssh_exception.NetmikoAuthenticationException:
            pbar.write(f'Не удалось подключиться к NE c IP-адресом {v_ne_ip}. Ошибка аутентификации.')
            v_report[v_counter-1]['status'] = 'Auth. error'
        else:
            try:
                os.mkdir(v_path + '\\' + f"NE-{v_counter} (" + v_ne_ip + ")")
            except OSError:
                print(f"Создать директорию не удалось")
            else:
                pass

            for i in enumerate(v_coms):
                v_filename: str = f"{v_nedir}" + r"\(" + f"{v_ne_ssh['host']})_{i[1]}.log"
                with open(v_filename, 'w') as f_output:
                    output = net_connect.send_command_timing(i[1], delay_factor=.5)
                    f_output.write(output)
                    output_splited = output.split('\n')
                    f_output.close()
                    v_out_msg = f"Успешное подключение к: {net_connect.find_prompt()}. SSH"

            v_report[v_counter - 1]['status'] = 'Ok'
            ''' Извлекаем hostname '''
            v_report[v_counter - 1]['hostname'] = net_connect.find_prompt(delay_factor=.5).strip('<>')
            ''' Извлекаем версмю ПО '''
            v_temp1 = net_connect.send_command_timing("display current-configuration | "
                                                      "include !Software", delay_factor=.5)
            v_report[v_counter - 1]['version'] = v_temp1.split()[-1]

            ''' Извлекаем версмю патча '''
            v_temp2 = net_connect.send_command_timing("display patch-information", delay_factor=.5)
            v_temp2_splited = v_temp2.split('\n')
            for v_str_patch in v_temp2_splited:
                if v_str_patch.find('Package Version') != -1:
                    v_report[v_counter - 1]['patch'] = v_str_patch.split(':')[-1]

            ''' Извлекаем P/N модели '''
            v_temp3 = net_connect.send_command_timing("display device", delay_factor=.5)
            v_temp3_splited = v_temp3.split('\n')
            v_report[v_counter - 1]['model'] = v_temp3_splited[0].split('\'')[0]

            net_connect.disconnect()
        v_counter += 1

        pbar.update(1)

""" Печать результата табличкой """
df = pandas.DataFrame.from_records(v_report)
df.fillna('-', inplace=True)
print('\n', df)


input('Готово. Для завершения программы нажмите Enter.')
