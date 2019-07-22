# TODO: Create pool

from deploy.config import Configuration
from deploy.pve import _qm_might_fail, get_all_vm_ids, pvesh, create_pool
from deploy.step import _init_swarm, _join_swarm, _install_docker, _post_creation, _create_qemu, _create_template_vm
from deploy.util import get_ips, _get_ssh_client


class Deployer:
    def __init__(self, cnf: Configuration):
        self.cnf = cnf

    def deploy(self):
        for i in range(self.cnf.worker_count):
            _qm_might_fail("stop {}".format(i + self.cnf.begin_id))
            _qm_might_fail("destroy {}".format(i + self.cnf.begin_id))
        _qm_might_fail("stop {}".format(9001))
        _qm_might_fail("destroy {}".format(9001))

        resources = pvesh("get /cluster/resources")
        all_ids = get_all_vm_ids(resources)

        if self.cnf.template_id in all_ids:
            raise RuntimeError("There already is a VM with the template ID in the cluster")
        _create_template_vm(self.cnf)

        create_pool(self.cnf.pool)

        vm_params = self._get_vm_parameters(all_ids)
        for i, proxmox_id, ip_address in vm_params:
            print("=> Creating VM {}".format(i))
            _create_qemu(self.cnf, i, proxmox_id, ip_address)

        swarm_key, swarm_ip = None, None
        for i, proxmox_id, ip_address in vm_params:
            print("=> Connecting to {}".format(ip_address))
            client = _get_ssh_client(ip_address, self.cnf.user)

            print("=> Installing docker on {}".format(ip_address))
            _install_docker(client)

            if i == 0:
                print("=> Init swarm on {}".format(ip_address))
                swarm_key, swarm_ip = _init_swarm(client, ip_address)
                print("Swarm key: {!r}".format(swarm_key))
                print("Swarm IP: {!r}".format(swarm_ip))
            else:
                _join_swarm(client, swarm_key, swarm_ip)
                pass

            client.close()

        master_ip = get_ips(self.cnf.ip_network, 1)[0]
        print("=> Running post-creation script on {}".format(master_ip))
        client = _get_ssh_client(master_ip, self.cnf.user)
        _post_creation(client)
        client.close()

    def _get_vm_parameters(self, all_ids):
        ip_addresses = get_ips(self.cnf.ip_network, self.cnf.worker_count)
        proxmox_ids = [self.cnf.begin_id + i for i in range(self.cnf.begin_id)]

        params = []
        for i, proxmox_id, ip in zip(range(self.cnf.worker_count), proxmox_ids, ip_addresses):
            if ip in all_ids:
                raise RuntimeError("VM with ID={} is already in the cluster".format(proxmox_id))
            params.append((i, proxmox_id, ip))

        return params


if __name__ == '__main__':
    config = Configuration(
        worker_count=5,

        network_interface='vmbr1337',
        ip_network='10.33.0.0/24',  # IP Network for node addresses.
        nameserver='157.159.10.12',

        user='deploy',
        ssh_key='~/.ssh/id_rsa.pub',

        begin_id=1000,
        template_id=9001,
        vm_name=lambda i: "docker{}".format(i),
        vm_description=lambda i: "Docker swarm worker {}".format(i),
        pool='dockerswarm',

        template_cloudinit_url='https://cloud-images.ubuntu.com/bionic/current/bionic-server-cloudimg-amd64.img',
        download_path='~/',
        ram_mb=2048,
        disk_size_gb=10,
        template_storage='nfs-cody',
        sockets=4,
    )

    Deployer(config).deploy()
