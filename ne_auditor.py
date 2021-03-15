"""
NE_auditor v.05
Скрипт для аудита сети.
"""


import datetime
import getpass
import os
import shutil
import argparse
import pandas  # для табличного отчёта
import tqdm
from netmiko import ssh_exception, ConnectHandler, SSHDetect
from ip_list_checker import f_ip_list_checker


def f_commands_reader(commands_file):
    coms = ()  # определяем список команд
    try:
        with open(commands_file, 'r') as commreader:
            v_line: str = commreader.readline()
            while v_line:
                coms = coms + (v_line.rstrip(),)
                v_line = commreader.readline()
            coms = tuple(set(coms))  # дедубликация команд
    except FileNotFoundError:
        print(f"Ошибка: файл ./{v_commands_file}, содержащий построчный список команд, не найден.")
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


def f_comand_outputs_to_files(comands_list, ne_ip, directory_name, net_connect):
    for i in enumerate(comands_list):
        v_filename: str = f"{directory_name}" + r"\(" + f"{ne_ip})_{i[1]}.log"
        with open(v_filename, 'w') as f_output:
            output = net_connect.send_command_timing(i[1], delay_factor=5)
            f_output.write(output)
            f_output.close()


def f_device_caller(device_list, login, password):
    counter: int = 0
    for v_ne_ip in device_list:
        v_ne = f"NE-{counter}"
        v_nedir = v_path + '\\' + f"{v_ne} (" + v_ne_ip + ")"
        v_ne_ssh = {
            'device_type': 'autodetect',
            'ip': v_ne_ip,
            'username': login,
            'password': password,
            'conn_timeout': 15
        }
        v_report.append(v_ne_status.copy())
        v_report[counter]['ip'] = v_ne_ssh["ip"]

        try:
            net_connect = ConnectHandler(**v_ne_ssh)
        except ssh_exception.NetmikoTimeoutException:
            pbar.write(f'Не удалось подключиться к {v_ne_ssh["ip"]}. Хост недоступен по SSH.')
            v_report[counter]['status'] = 'No access'
        except ssh_exception.NetmikoAuthenticationException:
            pbar.write(f'Не удалось подключиться к {v_ne_ssh["ip"]}. Ошибка аутентификации.')
            v_report[counter]['status'] = 'Auth. error'
        else:
            guesser = SSHDetect(**v_ne_ssh)
            v_report[counter]['device_type'] = guesser.autodetect()
            f_dir_creator(v_path + '\\' + f"NE-{counter} (" + v_ne_ssh["ip"] + ")")
            f_comand_outputs_to_files(v_coms, v_ne_ssh["ip"], v_nedir, net_connect)
            ''' Подготовка отчёта '''
            v_report[counter]['status'] = 'Ok'
            v_report[counter]['hostname'] = net_connect.find_prompt().strip('<>#')
        counter += 1


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--network-elements-list", action="store", dest="n",
                        help="Файл со списком сетевых элементов (NE)", default="ne_list.txt")
    parser.add_argument("-c", "--command-list", action="store", dest="c",
                        help="Файл со списком консольных команд для сетевых элементов (NE)", default="ne_commands.txt")
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

    with tqdm.tqdm(total=len(v_nes), desc="Обработано NE") as pbar:  # ПОЧИНИТЬ
        f_device_caller(v_nes, v_login, v_pass)
        pbar.update(1)

    """ Печать результата табличкой """
    df = pandas.DataFrame.from_records(v_report)
    df.fillna('-', inplace=True)
    print('\n', df)
    df.to_csv(str(v_path) + r'\AuditReport.csv', index=False)

    input('\nГотово. Для завершения программы нажмите Enter.')
