import ipaddress
import os
from typing import Callable


class Configuration:
    def __init__(
            self,
            worker_count: int,

            # NETWORKING OPTIONS:
            network_interface: str,  # Bridge interface used by workers.
            nameserver: str,  # DNS server.
            # IP network where IP from workers will be picked. First IP that is not the IP of the network will be the
            # gateway.
            ip_network: str,

            # WORKER VM OPTIONS:
            user: str,  # User that can be used to SSH on the worker.
            ssh_key: str,  # SSH key that can be used to SSH on the worker (must be unencrypted).

            # PROXMOX OPTIONS:
            begin_id: int,  # Proxmox ID for the first worker, other workers will be created with sequential IDs.
            template_id: int,  # Proxmox ID for the template.
            vm_name: Callable[[int], str],  # Function that returns the name of a VM.
            vm_description: Callable[[int], str],  # Function that returns the description of a VM.
            pool: str,  # Proxmox pool that will be created and used for these workers.
            template_storage: str,  # Where the VMs will be stored (must be a proxmox storage name).

            # CLOUDINIT OPTIONS:
            download_path: str,  # Folder where the CloudInit template will be downloaded.
            # URL to a CloudInit template (do not use minimal install as they lack vxlan kernel option)
            template_cloudinit_url: str,

            # VM OPTIONS:
            ram_mb: int,  # RAM in megabytes.
            disk_size_gb: int,  # Disk size in gigabytes.
            sockets: int  # vCPU per VM.
    ):
        assert worker_count >= 2, "must have at least 2 nodes"
        self.worker_count = worker_count
        self.network_interface = network_interface
        self.ip_network = ipaddress.ip_network(ip_network)
        self.gateway = next(self.ip_network.hosts())
        self.nameserver = ipaddress.ip_address(nameserver)
        self.user = user
        self.ssh_key = os.path.expanduser(ssh_key)
        self.begin_id = begin_id
        self.template_id = template_id
        self.vm_name = vm_name
        self.vm_description = vm_description
        self.pool = pool
        self.template_cloudinit_url = template_cloudinit_url
        self.download_path = os.path.expanduser(download_path)
        self.ram_nb = ram_mb
        self.disk_size_gb = disk_size_gb
        self.template_storage = template_storage
        self.sockets = sockets
