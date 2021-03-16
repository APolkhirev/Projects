"""
NE_auditor v.05
Скрипт для аудита сети.
"""

import yaml
import datetime
import getpass
import os
import shutil
import argparse
import pandas  # для табличного отчёта
import tqdm
from pprint import pprint
from netmiko import ssh_exception, ConnectHandler, SSHDetect
from ip_list_checker import f_ip_list_checker


def f_commands_reader(commands_file):
    try:
        with open(commands_file, 'r') as commreader:
            coms = yaml.safe_load(commreader)
            # pprint(coms)
    except FileNotFoundError:
        print(f"Ошибка: файл ./{v_commands_file}, в формате YAML, не найден.")
    return coms


def f_dir_creator(dir_name):
    try:
        shutil.rmtree(dir_name, ignore_errors=False, onerror=None)
    except OSError:
        pass

    try:
        os.mkdir(dir_name)
    except OSError:
        print(f"Создать директорию {dir_name} не удалось")


def f_comand_outputs_to_files(comands_list, ne_ip, directory_name, net_connect, dev_type):
    c_list = tuple(sorted(comands_list[dev_type]))
    for i in enumerate(c_list):
        v_filename: str = f"{directory_name}" + r"\(" + f"{ne_ip})_{i[1]}.log"
        with open(v_filename, 'w') as f_output:
            output = net_connect.send_command_timing(i[1], delay_factor=5)
            f_output.write(output)
            f_output.close()


def f_device_caller(device_list, cons_comm, login, password):
    counter: int = 0
    for v_ne_ip in device_list:
        v_ne = f'NE-{counter}'
        v_nedir = v_path + '\\' + f'{v_ne} (' + v_ne_ip + ')'
        v_ne_ssh = {
            'device_type': 'autodetect',
            'ip': v_ne_ip,
            'username': login,
            'password': password,
            'conn_timeout': 15
        }
        v_report.append(v_ne_status.copy())
        v_report[counter]['ip'] = v_ne_ip

        try:
            guesser = SSHDetect(**v_ne_ssh)
            v_dtype = guesser.autodetect()
            v_ne_ssh['device_type'] = v_dtype
            net_connect = ConnectHandler(**v_ne_ssh)
        except ssh_exception.NetmikoAuthenticationException:
            pbar.write(f'Не удалось подключиться к {v_ne_ip}. Ошибка аутентификации.')
            v_report[counter]['status'] = 'Auth. error'
            pbar.update(1)
        except ssh_exception:
            pbar.write(f'Не удалось подключиться к {v_ne_ip}. Хост недоступен по SSH.')
            v_report[counter]['status'] = 'No SSH access'
            pbar.update(1)
        else:
            f_dir_creator(v_path + '\\' + f"NE-{counter} ({v_ne_ip})")
            f_comand_outputs_to_files(cons_comm, v_ne_ip, v_nedir, net_connect, v_dtype)
            v_report[counter]['status'] = 'Ok'
            v_report[counter]['hostname'] = net_connect.find_prompt().strip('<>#')
            v_report[counter]['device_type'] = v_dtype
            net_connect.disconnect()
            pbar.update(1)
        counter += 1


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--network-elements-list", action="store", dest="n",
                        help="Файл со списком сетевых элементов (NE)", default="ne_list.txt")
    parser.add_argument("-c", "--command-list", action="store", dest="c",
                        help="Файл со списком консольных команд для сетевых элементов (NE)", default="ne_commands.yml")
    args = parser.parse_args()
    v_ip_list_file: str = args.n
    v_commands_file: str = args.c

    v_nes = f_ip_list_checker(v_ip_list_file)  # определяем список NE
    v_ne_status = dict.fromkeys(['hostname', 'ip', 'device_type', 'status'])
    v_report = []

    v_path: str = './audit_result_' + str(datetime.date.today())
    f_dir_creator(v_path)
    v_coms = f_commands_reader(v_commands_file)  # Считываем команды из файла в переменную

    v_login = input("Введите логин (общий на все NE): ")
    v_pass: str = ''
    try:
        v_pass = getpass.getpass("Введите пароль: ")
        print('='*15, 'СТАРТ', '='*15)
    except Exception as err:
        print('Ошибка: ', err)

    with tqdm.tqdm(total=len(v_nes), desc="Обработано NE") as pbar:
        f_device_caller(v_nes, v_coms, v_login, v_pass)

    """ Вывод отчёта """
    df = pandas.DataFrame.from_records(v_report)
    df.fillna('-', inplace=True)
    pprint(df)
    df.to_csv(str(v_path) + r'\AuditReport.csv', index=False)

    input('\nГотово. Для завершения программы нажмите Enter.')
