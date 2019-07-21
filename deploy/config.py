import ipaddress
import os


class Configuration:
    def __init__(
            self,
            count: int,
            network_interface: str,
            network: str,
            gateway: str,
            nameserver: str,
            user: str,
            ssh_key: str,
            begin_id: int,
            template_id: int,
            vm_name: callable,
            vm_description: callable,
            pool: str,
            template_cloudinit_url: str,
            working_path: str,
            ram_mb: int,
            disk_size_gb: int,
            template_storage: str,
            default_address_pool: str,
    ):
        assert count >= 2, "must have at least 2 nodes"
        self.count = count
        self.network_interface = network_interface
        self.network = ipaddress.ip_network(network)
        self.gateway = ipaddress.ip_address(gateway)
        self.nameserver = ipaddress.ip_address(nameserver)
        self.user = user
        self.ssh_key = os.path.expanduser(ssh_key)
        self.begin_id = begin_id
        self.template_id = template_id
        self.vm_name = vm_name
        self.vm_description = vm_description
        self.pool = pool
        self.template_cloudinit_url = template_cloudinit_url
        self.working_path = os.path.expanduser(working_path)
        self.ram_nb = ram_mb
        self.disk_size_gb = disk_size_gb
        self.template_storage = template_storage
        self.default_address_pool = ipaddress.ip_network(default_address_pool)

