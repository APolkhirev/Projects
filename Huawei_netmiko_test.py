from netmiko import ssh_exception
from netmiko.huawei.huawei import HuaweiSSH
from netmiko.huawei.huawei import HuaweiTelnet


v_session = {
    "ip": '10.158.149.10',
    "username": 'auditor',
    "password": '1qaz@WSX'
    #"device_type": 'huawei',
    #"global_delay_factor": 0.1,  # Increase all sleeps by a factor of 1
}
v_telnet = {
    "ip": '10.158.149.11',
    "username": 'auditor',
    "password": '1qaz@WSX',
    #"device_type": 'huawei',
    #"global_delay_factor": 0.1,  # Increase all sleeps by a factor of 1
}

net_connect = HuaweiTelnet(**v_session)
output = net_connect.send_command_timing('display users')
print(output)
