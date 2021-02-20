from netmiko import (Netmiko, ssh_exception)

def f_ne_access(v_host_ip, v_username, v_password, v_vendor, v_coms, v_nedir):
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
        print(f'Не удалось подключиться к NE c адресом {v_ne_ssh["host"]}')
        return 'Не доступен'
    else:
        print("Connected to:", net_connect.find_prompt())
        while v_comand in v_coms:
            v_filename: str = v_nedir + "\\" + "(" + x + ")_" + v_comand + ".log"
            with open(v_filename, 'w') as f_output:
                output = net_connect.send_command_timing(v_ne_ssh[v_comand])
                f_output.write(output)
                f_output.close()
        net_connect.disconnect()
        return 'SSH'
