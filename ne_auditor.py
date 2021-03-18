"""
NE_auditor v0.6
Скрипт для аудита сети.
"""

import yaml
import datetime
import getpass
import os
import sys
import shutil
import argparse
import pandas
import time
import random
from tabulate import tabulate
#  import tqdm
from netmiko import ssh_exception, ConnectHandler, SSHDetect
from concurrent.futures import ThreadPoolExecutor
import logging
from ip_list_checker import f_ip_list_checker


def f_commands_reader(commands_file):
    commands_reader_err_msg = '{} The ./{} file in YAML format was not found.'
    try:
        with open(commands_file, 'r') as commreader:
            coms = yaml.safe_load(commreader)
    except FileNotFoundError:
        logging.info(commands_reader_err_msg.format(datetime.datetime.now().time(), v_commands_file))
        sys.exit(1)
    return coms


def f_dir_creator(dir_name):
    dir_creator_err_msg = '{} Failed to create a directory: {}'
    try:
        shutil.rmtree(dir_name, ignore_errors=False, onerror=None)
    except OSError:
        pass

    try:
        os.mkdir(dir_name)
    except OSError:
        logging.info(dir_creator_err_msg.format(datetime.datetime.now().time(), dir_name))


def f_comand_outputs_to_files(comands_list, ne_ip, directory_name, net_connect, dev_type):
    cmdsend_msg = "---> {} Push:       {} / '{}'"
    c_list = tuple(sorted(comands_list[dev_type]))
    for i in enumerate(c_list):
        v_filename: str = f"{directory_name}" + r"/(" + f"{ne_ip})_{i[1]}.log"
        with open(v_filename, 'w') as f_output:
            logging.info(cmdsend_msg.format(datetime.datetime.now().time(), ne_ip, i[1]))
            output = net_connect.send_command_timing(i[1], delay_factor=5)
            f_output.write(output)
            f_output.close()


def f_send_commands_to_device(id_count: int, device, command_set, nedir):
    ip = device['ip']
    start_msg = '===> {} Connection: {}'
    received_msg = '<=== {} Received:   {}'
    received_err_msg = '<~~~ {} Received:   {} / {}'
    time.sleep(0.1 * random.randint(1, 3) + (id_count % 10)*0.3)
    logging.info(start_msg.format(datetime.datetime.now().time(), ip))
    try:
        guesser = SSHDetect(**device)
        v_dtype = guesser.autodetect()
        device['device_type'] = v_dtype
        net_connect = ConnectHandler(**device)
    except ssh_exception.NetmikoAuthenticationException:
        v_report[id_count]['status'] = 'Auth. error'
        logging.info(received_err_msg.format(datetime.datetime.now().time(), ip, 'Authentication error'))
    except ssh_exception:
        v_report[id_count]['status'] = 'No SSH access'
        logging.info(received_err_msg.format(datetime.datetime.now().time(), ip, 'SSH access error'))
    else:
        f_dir_creator(v_path + f"/NE-{id_count} ({ip})")
        f_comand_outputs_to_files(command_set, ip, nedir, net_connect, v_dtype)
        logging.info(received_msg.format(datetime.datetime.now().time(), ip))
        v_report[id_count]['status'] = 'Ok'
        v_report[id_count]['hostname'] = net_connect.find_prompt().strip('<>#')
        v_report[id_count]['device_type'] = v_dtype
        net_connect.disconnect()


def f_device_caller(device_list, cons_comm, login, password):
    counter: int = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
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
            executor.submit(f_send_commands_to_device, counter, v_ne_ssh, cons_comm, v_nedir)
            counter += 1


if __name__ == '__main__':

    logging.getLogger("paramiko").setLevel(logging.WARNING)
    logging.basicConfig(
        format='%(threadName)s %(name)s %(levelname)s: %(message)s',
        level=logging.INFO)

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

    v_login = input("Login: ")
    v_pass: str = ''
    try:
        v_pass = getpass.getpass("Password: ")
        print('\nStart:')
    except Exception as err:
        print('Ошибка: ', err)

    f_device_caller(v_nes, v_coms, v_login, v_pass)
    print('Stop.\n')

    df = pandas.DataFrame(v_report)
    df.fillna('-', inplace=True)
    print(tabulate(df, headers='keys', tablefmt='rst'))
    df.to_csv(str(v_path) + r'\AuditReport.csv', index=False)

    input('\nDone. Press ENTER to exit.')
