"""
NE_auditor v.04
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

    v_counter: int = 1
    with tqdm.tqdm(total=len(v_nes), desc="Обработано NE") as pbar:
        for v_ne_ip in v_nes:
            v_ne = f"NE-{v_counter}"
            v_nedir = v_path + '\\' + f"{v_ne} (" + v_ne_ip + ")"
            v_out_msg = ''
            v_ne_ssh = {
                'device_type': 'autodetect',
                'ip': v_ne_ip,
                'username': v_login,
                'password': v_pass,
                'conn_timeout': 15
             }
            v_report.append(v_ne_status.copy())
            v_report[v_counter-1]['ip'] = v_ne_ip

            try:
                net_connect = ConnectHandler(**v_ne_ssh)
            except ssh_exception.NetmikoTimeoutException:
                pbar.write(f'Не удалось подключиться к {v_ne_ip}. Хост недоступен по SSH.')
                v_report[v_counter-1]['status'] = 'No access'
            except ssh_exception.NetmikoAuthenticationException:
                pbar.write(f'Не удалось подключиться к {v_ne_ip}. Ошибка аутентификации.')
                v_report[v_counter-1]['status'] = 'Auth. error'
            else:
                guesser = SSHDetect(**v_ne_ssh)
                v_report[v_counter - 1]['device_type'] = guesser.autodetect()

                f_dir_creator(v_path + '\\' + f"NE-{v_counter} (" + v_ne_ip + ")")
#
                for i in enumerate(v_coms):
                    v_filename: str = f"{v_nedir}" + r"\(" + f"{v_ne_ip})_{i[1]}.log"
                    with open(v_filename, 'w') as f_output:
                        output = net_connect.send_command_timing(i[1], delay_factor=5)
                        f_output.write(output)
                        f_output.close()
                        v_out_msg = f"Успешное подключение к: {net_connect.find_prompt()}. SSH"

                ''' Подготовка отчёта '''
                v_report[v_counter - 1]['status'] = 'Ok'
                v_report[v_counter - 1]['hostname'] = net_connect.find_prompt().strip('<>#')

            v_counter += 1
            pbar.update(1)

    """ Печать результата табличкой """
    df = pandas.DataFrame.from_records(v_report)
    df.fillna('-', inplace=True)
    print('\n', df)
    df.to_csv(str(v_path) + r'\AuditReport.csv', index=False)

    input('\nГотово. Для завершения программы нажмите Enter.')
