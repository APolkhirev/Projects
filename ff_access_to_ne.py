from netmiko import (Netmiko, ssh_exception)

def f_ne_access(v_host_ip, v_username, v_password, v_vendor, v_command):
    """
    вывод команд
    """

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
        print(f'Не удалось подключиться к {v_ne_ssh["host"]}')
    else:
        print("Connected to:", net_connect.find_prompt())
        output = net_connect.send_command_timing(v_ne_ssh[v_command])
        net_connect.disconnect()
        return output
