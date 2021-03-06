"""
A module for checking the list of IP addresses.
v1.1
"""

import ipaddress
import logging
import os

logger = logging.getLogger(__name__)


def f_message(messtext: str) -> str:
    return str(messtext + " " + "•" * (os.get_terminal_size()[0] - len(messtext) - 2))


def f_check_ip(v_ip: str) -> tuple[bool, str]:
    """
    Checking the IP address for the destination on the interface.
    The script checks both the format and ownership of the reserved pool of addresses
    that cannot be used for this purpose.
    """
    try:
        ipaddress.ip_address(v_ip)
    except (ipaddress.AddressValueError, ValueError):
        return False, "Invalid IP-address format."
    if ipaddress.IPv4Address(v_ip).is_link_local:
        return (
            False,
            "Bad IP: Used for link-local addresses between two hosts on a single link when no IP "
            "address is otherwise specified, such as would have normally been retrieved from a DHCP server.",
        )
    elif ipaddress.IPv4Address(v_ip).is_loopback:
        return False, "Bad IP: Used for loopback addresses to the local host."
    elif ipaddress.ip_address(v_ip) == ipaddress.ip_address("255.255.255.255"):
        return (
            False,
            "Bad IP: Reserved for the limited broadcast destination address.",
        )
    elif ipaddress.IPv4Address(v_ip).is_multicast:
        return False, "Bad IP: In use for IP multicast."
    elif ipaddress.IPv4Address(v_ip).is_link_local:
        return (
            False,
            "Bad IP: The address is reserved for link-local usage. See RFC 3927.",
        )
    elif ipaddress.IPv4Address(v_ip).is_unspecified:
        return (
            False,
            "Bad IP: The IP address is unspecified. See RFC 5735 (for IPv4) or RFC 2373 (for IPv6).",
        )
    elif (
        ipaddress.ip_address("0.0.0.0")
        < ipaddress.ip_address(v_ip)
        < ipaddress.ip_address("0.255.255.255")
    ):
        return False, "Bad IP: Current network (only valid as source address)."
    elif (
        ipaddress.ip_address("100.64.0.0")
        < ipaddress.ip_address(v_ip)
        < ipaddress.ip_address("100.127.255.255")
    ):
        return (
            False,
            "Bad IP: Shared address space for communications between a service provider and "
            "its subscribers when using a carrier-grade NAT.",
        )
    elif (
        ipaddress.ip_address("192.0.0.0")
        < ipaddress.ip_address(v_ip)
        < ipaddress.ip_address("192.0.0.255")
    ):
        return False, "Bad IP: IETF Protocol Assignments."
    elif (
        ipaddress.ip_address("192.0.2.0")
        < ipaddress.ip_address(v_ip)
        < ipaddress.ip_address("192.0.2.255")
    ):
        return False, "Bad IP: Assigned as TEST-NET-1, documentation and examples."
    elif (
        ipaddress.ip_address("192.31.196.0")
        < ipaddress.ip_address(v_ip)
        < ipaddress.ip_address("192.31.196.255")
    ):
        return False, "Bad IP: AS112-v4."
    elif (
        ipaddress.ip_address("192.52.193.0")
        < ipaddress.ip_address(v_ip)
        < ipaddress.ip_address("192.52.193.255")
    ):
        return False, "Bad IP: AMT."
    elif (
        ipaddress.ip_address("192.88.99.0")
        < ipaddress.ip_address(v_ip)
        < ipaddress.ip_address("192.88.99.0")
    ):
        return False, "Bad IP: Reserved. Formerly used for IPv6 to IPv4 relay."
    elif (
        ipaddress.ip_address("192.175.48.0")
        < ipaddress.ip_address(v_ip)
        < ipaddress.ip_address("192.175.48.0")
    ):
        return False, "Bad IP: Direct Delegation AS112 Service."
    elif (
        ipaddress.ip_address("198.18.0.0")
        < ipaddress.ip_address(v_ip)
        < ipaddress.ip_address("198.19.255.255")
    ):
        return (
            False,
            "Bad IP: Used for benchmark testing of inter-network communications "
            "between two separate subnets.",
        )
    elif (
        ipaddress.ip_address("198.51.100.0")
        < ipaddress.ip_address(v_ip)
        < ipaddress.ip_address("198.51.100.255")
    ):
        return False, "Bad IP: Assigned as TEST-NET-2, documentation and examples."
    elif (
        ipaddress.ip_address("203.0.113.0")
        < ipaddress.ip_address(v_ip)
        < ipaddress.ip_address("203.0.113.255")
    ):
        return False, "Bad IP: Assigned as TEST-NET-3, documentation and examples."

    return True, "IP address is valid"


def f_ip_list_checker(v_ip_list_file: str) -> list[str]:
    v_nes: list[str] = []
    v_counter: int = 0

    try:
        with open(v_ip_list_file, "r") as v_ip_reader:
            v_ip: str = v_ip_reader.readline()
            while v_ip:
                v_counter += 1
                if f_check_ip(v_ip.rstrip())[0]:
                    v_nes = v_nes + [
                        v_ip.rstrip(),
                    ]
                else:
                    mes_txt: str = (
                        f"WARNING In the file '{v_ip_list_file}', line {v_counter} "
                        f"(IP '{v_ip.rstrip()}'): {f_check_ip(v_ip.rstrip())[1]}"
                    )
                    logger.warning(f_message(mes_txt))
                v_ip = v_ip_reader.readline()
            v_list_len: int = len(v_nes)
            v_nes = sorted(set(v_nes), key=ipaddress.IPv4Address)

            diff_len: int = v_list_len - len(v_nes)
            if diff_len != 0:
                logger.warning(
                    f_message(
                        f"INFO: Duplicate addresses were removed from the file '{v_ip_list_file}': {diff_len}"
                    )
                )
    except FileNotFoundError:
        logger.error(
            f_message(
                f"ERROR: The file './{v_ip_list_file}' with the IP-address list was not found."
            )
        )
    return v_nes


if __name__ == "__main__":
    print(f_ip_list_checker("ne_list.ini"))
