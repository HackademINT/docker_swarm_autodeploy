import json
import subprocess
from typing import Set


def pvesh(cmd: str) -> dict:
    json_result = subprocess.Popen("pvesh " + cmd + " --output=json", shell=True, stdout=subprocess.PIPE).stdout.read()
    return json.loads(json_result.decode())


def get_all_vm_ids(resources: dict) -> Set[int]:
    return set(res['vmid'] for res in resources if 'vmid' in res)


def filter_qemu(resources: dict):
    return [res for res in resources if res.get("type") == "qemu"]


def qm(s: str):
    if not _qm_might_fail(s):
        raise RuntimeError('subprocess.call returned non-zero error code')


def create_pool(name: str):
    subprocess.call('pvesh create /pools --poolid {!r}'.format(name), shell=True)


def _qm_might_fail(s: str) -> bool:
    """
    Execute the command and return true on success.
    :param s:
    :return:
    """
    cmd = 'qm {}'.format(s)
    print('==> Running {!r}'.format(cmd))
    return not bool(subprocess.call(cmd, shell=True))
