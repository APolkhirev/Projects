"""
NE_auditor v0.8
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

import enlighten
import pandas
import yaml
from netmiko import ssh_exception, ConnectHandler, SSHDetect
from tabulate import tabulate

from ip_list_checker import f_ip_list_checker


MAX_CONCURRENT_SESSIONS = 10
DEFAULT_UFO_DEVICE_TYPE = "eltex"


def f_commands_reader(commands_file):
    commands_reader_err_msg = "The file './{}' in YAML format was not found."

    try:
        with open(commands_file, "r") as command_reader:
            commands = yaml.safe_load(command_reader)
    except FileNotFoundError:
        logging.error(commands_reader_err_msg.format(v_commands_file))
        sys.exit(1)
    return commands


def f_dir_creator(dir_name):
    dir_creator_err_msg = "{} Failed to create a directory: {}"

    try:
        shutil.rmtree(dir_name, ignore_errors=False, onerror=None)
    except OSError:
        pass

    try:
        os.mkdir(dir_name)
    except OSError:
        logging.warning(
            dir_creator_err_msg.format(datetime.datetime.now().time(), dir_name)
        )


def f_command_outputs_to_files(
    commands_list, ne_ip, directory_name, net_connect, dev_type
):
    cmd_send_msg = "---> {} Push:       {}   / {}: {}"
    c_list = tuple(sorted(commands_list[dev_type]))

    for i in enumerate(c_list):
        v_filename: str = (
            f"{directory_name}/({ne_ip})_{str(i[1]).replace('|', 'I')}.log"
        )
        with open(v_filename, "w") as f_output:
            logging.info(
                cmd_send_msg.format(
                    datetime.datetime.now().time(), ne_ip, dev_type, i[1]
                )
            )
            output = net_connect.send_command_timing(i[1], delay_factor=5)
            f_output.write(output)
            f_output.close()


def f_send_commands_to_device(
    id_count: int, device, command_set, nedir, v_pbar, ufo_type
):
    ip = device["ip"]
    start_msg = "===> {} Connection: {}"
    received_msg = "<=== {} Received:   {}"
    received_err_msg = "<~~~ {} Received:   {}   / {}"
    time.sleep(0.1 * random.randint(0, 3) + (id_count % 10) * 0.33)
    logging.info(start_msg.format(datetime.datetime.now().time(), ip))

    try:
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
    except ssh_exception.NetmikoAuthenticationException:
        v_report[id_count]["status"] = "Auth. error"
        logging.info(
            received_err_msg.format(
                datetime.datetime.now().time(), ip, "Authentication error"
            )
        )
        v_pbar.update()
    except ssh_exception:
        v_report[id_count]["status"] = "No SSH access"
        logging.info(
            received_err_msg.format(
                datetime.datetime.now().time(), ip, "SSH access error"
            )
        )
        v_pbar.update()
    else:
        f_dir_creator(v_path + f"/NE-{id_count} ({ip})")
        f_command_outputs_to_files(command_set, ip, nedir, net_connect, v_dtype)
        logging.info(received_msg.format(datetime.datetime.now().time(), ip))
        v_report[id_count]["status"] = "Ok"
        v_report[id_count]["hostname"] = net_connect.find_prompt().strip("<>#")
        v_report[id_count]["device_type"] = v_dtype
        v_pbar.update()
        net_connect.disconnect()


def f_device_caller(device_list, cons_comm, login, password, ufo_type):
    counter: int = 0
    manager = enlighten.get_manager()
    pbar = manager.counter(
        total=len(device_list), desc="Devices processed:", unit="NE", color="red"
    )
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

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n",
        "--network-elements-list",
        dest="n",
        action="store",
        help="The name of the file with the list of network elements (NE)",
        default="ne_list.txt",
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

    logging.getLogger("paramiko").setLevel(logging.WARNING)
    logging.basicConfig(
        format="%(threadName)s %(name)s %(levelname)s: %(message)s",
        level=logging.INFO,
    )

    v_nes = f_ip_list_checker(v_ip_list_file)
    v_ne_status = dict.fromkeys(["hostname", "ip", "device_type", "status"])
    v_report = []

    v_path: str = "./audit_result_" + str(datetime.date.today())
    f_dir_creator(v_path)
    v_coms = f_commands_reader(v_commands_file)

    v_login = input("Login: ")
    v_pass: str = ""

    try:
        v_pass = getpass.getpass("Password: ")
        print("\nStart:")
    except Exception as err:
        print("Error: ", err)

    f_device_caller(v_nes, v_coms, v_login, v_pass, v_ufo_type)
    print("Stop.\n")

    df = pandas.DataFrame(v_report)
    df.fillna("-", inplace=True)
    print(tabulate(df, headers="keys", tablefmt="rst"))
    df.to_csv(str(v_path) + r"\AuditReport.csv", index=False)

    input("\nDone. Press ENTER to exit.")
