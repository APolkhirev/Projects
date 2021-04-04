"""
NE_auditor v1.1
"""

import argparse
import datetime
import getpass
import logging
import os
import random
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Union

import enlighten
import pandas
import yaml
from netmiko import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
    ConnectHandler,
    SSHDetect,
)
from paramiko import ssh_exception
from tabulate import tabulate

from ip_list_checker import f_ip_list_checker
from retry import retry


DEFAULT_UFO_DEVICE_TYPE: str = "extreme"
MAX_CONCURRENT_SESSIONS: int = 10
RETRY_TIMES: int = 2

manager = enlighten.get_manager()
pbar = manager.counter(total=0, desc="Devices processed:", unit="NE", color="red")


def f_message(messtext: str) -> None:
    print("\n" + messtext, "*" * (os.get_terminal_size()[0] - len(messtext) - 2))


def f_commands_reader(commands_file: str) -> dict[str, list[str]]:
    """ Считываение команд из YAML-файла в список """
    commands_reader_err_msg: str = "The file './{}' in YAML format was not found."

    try:
        with open(commands_file, "r") as command_reader:
            commands: dict[str, list[str]] = yaml.safe_load(command_reader)
    except FileNotFoundError:
        logging.error(commands_reader_err_msg.format(v_commands_file))
        f_message(
            f" ERROR: The file './{v_commands_file}' in YAML format was not found."
        )
        sys.exit(1)
    return commands


def f_dir_creator(dir_name: str) -> None:
    """ Безопасное создание дирректории """
    dir_creator_err_msg = "Failed to create a directory: {}"

    try:
        shutil.rmtree(dir_name, ignore_errors=False, onerror=None)
    except OSError:
        pass

    try:
        os.mkdir(dir_name)
    except OSError:
        logging.warning(dir_creator_err_msg.format(dir_name))
        f_message(f" INFO: Failed to create a directory: {dir_name}")


@retry(pbar, NetmikoTimeoutException, max_retries=RETRY_TIMES)
def f_send_commands_to_device(
    idx: int,
    device: dict[str, Union[str, int]],
    command_set: dict[str, list[str]],
    nedir: str,
    v_pbar,
    ufo_type: str,
) -> None:
    """
    Определение типа устройства, выбор для устройства перечня специфичных комманд
    и вызов вложенной функции ввода команд
    """

    def f_command_outputs_to_files() -> None:
        """ Применение списка команд на устройство и запись результатов в файл """
        cmd_send_msg: str = "---> Push:       {}   / {}: {}"
        c_list: tuple[str, ...] = tuple(sorted(command_set[v_dtype]))
        for i in enumerate(c_list):
            v_filename: str = f"{nedir}/({ip})_{str(i[1]).replace('|', 'I')}.log"
            with open(v_filename, "w") as f_output:
                logging.info(cmd_send_msg.format(ip, v_dtype, i[1]))
                f_message(f" TASK [{ip}  / {v_dtype}: {str(i[1])} ]")
                output = net_connect.send_command_timing(i[1], delay_factor=5)
                f_output.write(output)
                f_output.close()

    ip = device["ip"]
    start_msg: str = "===> Connection:    {}"
    received_msg: str = "<=== Received:   {}"
    received_err_msg: str = "<~~~ Received:   {}   / {}"

    time.sleep(
        0.1 * random.randint(0, 3) + (idx % 10) * 0.33
    )  # распределение группы сессий по небольшому интервалу времени
    logging.info(start_msg.format(ip))
    f_message(f" INFO [ Connection ===> {ip} ]")

    try:
        """ Определение типа устройства """
        guesser = SSHDetect(**device)
        v_dtype = guesser.autodetect()
        if v_dtype:
            device["device_type"] = v_dtype
        else:
            if ufo_type == "":
                device["device_type"] = DEFAULT_UFO_DEVICE_TYPE
                v_dtype = "UFO"
            else:
                device["device_type"] = ufo_type
                v_dtype = ufo_type
        net_connect = ConnectHandler(**device)
    except NetmikoAuthenticationException:
        v_pbar.update()
        v_report[idx]["status"] = "Authentication error"
        logging.warning(received_err_msg.format(ip, "Authentication error"))
        f_message(f" WARNING [ Received <~~~ {ip}   / Authentication error ]")
    except NetmikoTimeoutException:
        v_report[idx]["status"] = "Timeout error"
        logging.warning(received_err_msg.format(ip, "Timeout error"))
        f_message(f" WARNING [ Received <~~~ {ip}   / Timeout error ]")
        raise NetmikoTimeoutException
    except ssh_exception.SSHException:
        v_pbar.update()
        v_report[idx]["status"] = "SSH access error"
        logging.warning(received_err_msg.format(ip, "SSH access error"))
        f_message(f" WARNING [ Received <~~~ {ip}   / SSH access error ]")
    else:
        f_dir_creator(v_path + f"/NE-{idx} ({ip})")
        f_command_outputs_to_files()  # отправляем команды на устройство, считываем в соответствующие файлы
        v_pbar.update()
        logging.info(received_msg.format(ip))
        f_message(f" INFO [ Received <=== {ip} ]")
        v_report[idx]["status"] = "Ok"
        v_report[idx]["hostname"] = net_connect.find_prompt().strip("<>#")
        v_report[idx]["device_type"] = v_dtype
        net_connect.disconnect()


def f_device_caller(
    device_list: list[str],
    cons_comm: dict[str, list[str]],
    login: str,
    password: str,
    ufo_type: str,
) -> None:
    """Функция многопоточного опроса устройств из списка устройств"""
    counter: int = 0

    pbar.total = len(device_list)

    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_SESSIONS) as executor:
        for v_ne_ip in device_list:
            v_ne = f"NE-{counter}"
            v_nedir = f"{v_path}/{v_ne} ({v_ne_ip})"
            v_ne_ssh = {
                "device_type": "autodetect",
                "ip": v_ne_ip,
                "username": login,
                "password": password,
                "conn_timeout": 15,
            }
            v_report.append(v_ne_status.copy())
            v_report[counter]["ip"] = v_ne_ip
            # Отправка списка команд на устройство:
            executor.submit(
                f_send_commands_to_device,
                counter,
                v_ne_ssh,
                cons_comm,
                v_nedir,
                pbar,
                ufo_type,
            )
            counter += 1
            pbar.close()


if __name__ == "__main__":

    v_path: str = "./audit_result_" + str(datetime.date.today())
    f_dir_creator(v_path)

    logging.getLogger("paramiko").setLevel(logging.DEBUG)
    logging.basicConfig(
        format="%(asctime)s %(threadName)s %(name)s %(levelname)s: %(message)s",
        level=logging.INFO,
        filename=f"{v_path}/logfile.log",
    )

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n",
        "--network-elements-list",
        dest="n",
        action="store",
        help="The name of the file with the list of network elements (NE)",
        default="ne_list.ini",
    )
    parser.add_argument(
        "-c",
        "--command-list",
        dest="c",
        action="store",
        help="The name of the file with the list of commands for network elements (NE)",
        default="ne_commands.yml",
    )
    parser.add_argument(
        "-l",
        "--login",
        dest="l",
        action="store",
        help="Login name",
        default="",
    )
    parser.add_argument(
        "-p",
        "--password",
        dest="p",
        action="store",
        help="Login password",
        default="",
    )
    parser.add_argument(
        "-u",
        "--ufo-device",
        dest="u",
        action="store",
        help="The unknown NE type",
        default="",
    )
    args = parser.parse_args()
    v_ip_list_file: str = args.n
    v_commands_file: str = args.c
    v_ufo_type: str = args.u
    v_pass: str = args.p
    v_login: str = args.l
    if not v_login:
        v_login = input("Login: ")

    if not v_pass:
        try:
            v_pass = getpass.getpass("Password: ")
            f_message(f" PLAY [ '{v_commands_file}' for '{v_ip_list_file}' ]")
            logging.info("<" * 22 + "  START  " + ">" * 22)
        except Exception as err:
            f_message("Error: " + str(err))

    dev_param = {
        "device_type": "huawei",
        "ip": "10.158.149.10",
        "username": "auditor",
        "password": "1qaz@WS",
        "conn_timeout": 15,
    }

    v_nes: list[str] = f_ip_list_checker(v_ip_list_file)
    v_ne_status: dict[str, str] = dict.fromkeys(
        ["hostname", "ip", "device_type", "status"]
    )
    v_report: list[dict[str, str]] = []
    v_coms: dict[str, list[str]] = f_commands_reader(v_commands_file)

    logging.getLogger("paramiko").setLevel(logging.DEBUG)
    logging.basicConfig(
        format="%(threadName)s %(name)s %(levelname)s: %(message)s",
        level=logging.INFO,
        filename=f"{v_path}/logfile_{str(datetime.date.today())}.log",
        filemode="w",
    )

    f_device_caller(v_nes, v_coms, v_login, v_pass, v_ufo_type)
    f_message(" STOP")
    logging.info("<" * 22 + "  STOP  " + ">" * 22)

    df = pandas.DataFrame(v_report)
    df.fillna("-", inplace=True)
    print(tabulate(df, headers="keys", tablefmt="rst"))
    df.to_csv(str(v_path) + r"\AuditReport.csv", index=False)

    input("\nDone. Press ENTER to exit.")
