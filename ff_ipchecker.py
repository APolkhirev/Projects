import ipaddress

def f_checkip(v_ip):
    """
    Проверка валидности IP-адреса для назначения на интерфейсе. Скорипт проверяепт как формат, так и принадлежность
    зарезервированным пулам адресов.
    """
    try:
        ipaddress.ip_address(v_ip)
    except (ipaddress.AddressValueError, ValueError) as e:
        v_ip_description: str = 'Bad format.'
        return False, v_ip_description
    if ipaddress.ip_address('0.0.0.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('0.255.255.255'):
        v_ip_description = "Bad IP: Current network (only valid as source address)."
        return False, v_ip_description
    elif ipaddress.ip_address('100.64.0.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('100.127.255.255'):
        v_ip_description = """Bad IP: Shared address space for communications between a service provider and its 
        subscribers when using a carrier-grade NAT."""
        return False, v_ip_description
    elif ipaddress.ip_address('127.0.0.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('127.255.255.255'):
        v_ip_description = "Bad IP: Used for loopback addresses to the local host."
        return False, v_ip_description
    elif ipaddress.ip_address('169.254.0.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('169.254.255.255'):
        v_ip_description = """Bad IP: Used for link-local addresses between two hosts on a single link when no IP 
        address is otherwise specified, such as would have normally been retrieved from a DHCP server."""
        return False, v_ip_description
    elif ipaddress.ip_address('192.0.0.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('192.0.0.255'):
        v_ip_description = "Bad IP: IETF Protocol Assignments."
        return False, v_ip_description
    elif ipaddress.ip_address('192.0.2.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('192.0.2.255'):
        v_ip_description = "Bad IP: Assigned as TEST-NET-1, documentation and examples."
        return False, v_ip_description
    elif ipaddress.ip_address('192.31.196.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('192.31.196.255'):
        v_ip_description = "Bad IP: AS112-v4."
        return False, v_ip_description
    elif ipaddress.ip_address('192.52.193.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('192.52.193.255'):
        v_ip_description = "Bad IP: AMT."
        return False, v_ip_description
    elif ipaddress.ip_address('192.88.99.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('192.88.99.0'):
        v_ip_description = "Bad IP: Reserved. Formerly used for IPv6 to IPv4 relay."
        return False, v_ip_description
    elif ipaddress.ip_address('192.175.48.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('192.175.48.0'):
        v_ip_description = "Bad IP: Direct Delegation AS112 Service."
        return False, v_ip_description
    elif ipaddress.ip_address('198.18.0.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('198.19.255.255'):
        v_ip_description = """Bad IP: Used for benchmark testing of inter-network communications
        between two separate subnets."""
        return False, v_ip_description
    elif ipaddress.ip_address('198.51.100.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('198.51.100.255'):
        v_ip_description = "Bad IP: Assigned as TEST-NET-2, documentation and examples."
        return False, v_ip_description
    elif ipaddress.ip_address('203.0.113.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('203.0.113.255'):
        v_ip_description = "Bad IP: Assigned as TEST-NET-3, documentation and examples."
        return False, v_ip_description
    elif ipaddress.ip_address('224.0.0.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('239.255.255.255'):
        v_ip_description = "Bad IP: In use for IP multicast. (Former Class D network)."
        return False, v_ip_description
    elif ipaddress.ip_address('240.0.0.0') < ipaddress.ip_address(v_ip) < ipaddress.ip_address('255.255.255.254'):
        v_ip_description = "Bad IP: In use for IP multicast. Reserved for future use. (Former Class E network)."
        return False, v_ip_description
    elif ipaddress.ip_address(v_ip) == ipaddress.ip_address('255.255.255.255'):
        v_ip_description = """Bad IP: Reserved for the "limited broadcast" destination address."""
        return False, v_ip_description
    v_ip_description: str = 'IP address is valid'
    return True, v_ip_description
