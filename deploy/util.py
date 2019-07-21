import ipaddress
import itertools
import time
from typing import List

import paramiko

SLEEP = 5


def get_ips(network: ipaddress.IPv4Network, count: int) -> List[str]:
    return [
        str(ip) for ip in itertools.islice(network, 2, count + 2)
    ]


def _get_ssh_client(ip_address: str, username: str):
    while True:
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.WarningPolicy())
            client.connect(ip_address, username=username)
            client.exec_command("hostname")
            return client

        except paramiko.ssh_exception.NoValidConnectionsError as e:
            print(e)
            print(
                "Could not connect to {}, VM is probably not up yet, retrying in {} seconds.".format(ip_address, SLEEP))
            time.sleep(SLEEP)
