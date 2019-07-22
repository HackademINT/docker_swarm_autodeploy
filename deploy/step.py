import io
import os
import re
import urllib.request
from typing import Tuple

from deploy.config import Configuration
from deploy.pve import qm
from deploy.script import PROVISION_SCRIPT, POST_CREATE_SCRIPT

FILE_NAME = '/tmp/script.sh'
CLOUDINIT_IMG_NAME = 'cloudinit_template.img'


def _init_swarm(client, ip_address: str) -> Tuple[str, str]:
    _, stdout, _ = client.exec_command(
        "sudo docker swarm init --advertise-addr {}".format(ip_address))
    result = stdout.read().decode()
    match = re.search(r'--token (\S+) (\S+)', result)
    return match.group(1), match.group(2)


def _join_swarm(client, swarm_key: str, swarm_ip: str):
    _, stdout, _ = client.exec_command('sudo docker swarm join --token {} {}'.format(swarm_key, swarm_ip))
    print(stdout.read().decode())


def _install_docker(client):
    sftp = client.open_sftp()
    sftp.putfo(io.StringIO(PROVISION_SCRIPT), FILE_NAME)
    stdin, stdout, stderr = client.exec_command("bash {}".format(FILE_NAME))
    for line in iter(lambda: stdout.readline(2048), ""):
        print(line, end="")


def _post_creation(client):
    sftp = client.open_sftp()
    sftp.putfo(io.StringIO(POST_CREATE_SCRIPT), FILE_NAME)
    stdin, stdout, stderr = client.exec_command("bash {}".format(FILE_NAME))
    for line in iter(lambda: stdout.readline(2048), ""):
        print(line, end="")


def _create_qemu(cnf: Configuration, index: int, proxmox_id: int, ip_address: str) -> None:
    prefix_len = cnf.ip_network.prefixlen

    def qm_set(s):
        return qm('set {} {}'.format(proxmox_id, s))

    name = cnf.vm_name(index)
    description = cnf.vm_description(index)
    qm('clone {} {} '
       '--name {!r} '
       ' --description {!r} '
       '--pool {!r}'.format(cnf.template_id, proxmox_id, name, description, cnf.pool))
    qm_set('--net0 model=virtio,bridge={}'.format(cnf.network_interface))
    qm_set('--ipconfig0 ip={}/{},gw={}'.format(ip_address, prefix_len, cnf.gateway.exploded))
    qm_set('--nameserver {!r}'.format(cnf.nameserver.exploded))
    qm_set('--ciuser {!r}'.format(cnf.user))
    qm_set('--sshkey {!r}'.format(cnf.ssh_key))
    qm_set('--memory {}'.format(cnf.ram_nb))
    qm_set('--sockets {}'.format(cnf.sockets))
    qm_set('--agent 1')
    qm_set('--autostart 1')

    qm('resize {} {} {}G'.format(proxmox_id, 'scsi0', cnf.disk_size_gb))

    qm('start {}'.format(proxmox_id))


def _create_template_vm(cnf: Configuration):
    path = os.path.join(cnf.download_path, CLOUDINIT_IMG_NAME)

    print("=> Downloading CloudInit template image from {!r}".format(cnf.template_cloudinit_url))
    with urllib.request.urlopen(cnf.template_cloudinit_url) as response:
        with open(path, 'wb') as f:
            f.write(response.read())

    desc = 'Template for {} pool'.format(cnf.pool)
    qm('create {} --name Template --desc {!r} --pool {!r}'.format(cnf.template_id, desc, cnf.pool))
    qm('importdisk {} {} {}'.format(cnf.template_id, path, cnf.template_storage))
    qm('set {id} --scsihw virtio-scsi-pci --scsi0 {storage}:{id}/vm-{id}-disk-0.raw'.format(id=cnf.template_id,
                                                                                            storage=cnf.template_storage))
    qm('set {} --ide2 {}:cloudinit'.format(cnf.template_id, cnf.template_storage))
    qm('set {} --boot c --bootdisk scsi0'.format(cnf.template_id))
    qm('set {} --serial0 socket --vga serial0'.format(cnf.template_id))
    qm('template {}'.format(cnf.template_id))
