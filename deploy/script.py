
PROVISION_SCRIPT = """
while ! grep "Cloud-init .* finished" /var/log/cloud-init.log; do
    echo "$(date -Ins) Waiting for cloud-init to finish, this might take a while (~10 mins) since it is upgrading the whole system."
    echo "Retrying in 30 seconds."
    sleep 30
done

echo 'UPDATING'
sudo apt-get update

echo 'REMOVING POTENTIAL CONFLICTING PACKAGES'
sudo apt-get remove -y docker docker-engine docker.io containerd runc
echo 'INSTALLING DEPENDENCIES'
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common


echo 'ADDING DOCKER REPOSITORY'
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) \
    stable"

echo 'INSTALLING DOCKER'
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
sudo systemctl enable docker
sudo systemctl start docker

echo 'INSTALLING DOCKER-COMPOSE'
sudo curl -L "https://github.com/docker/compose/releases/download/1.23.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo 'INSTALLING QEMU GUEST AGENT'
sudo apt-get install -y qemu-guest-agent
"""

POST_CREATE_SCRIPT = """
echo 'Promoting every node to master'
sudo docker node ls | awk 'NR>1 {print $1}' | xargs sudo docker node promote

echo 'Adding a registry'
sudo docker service create --name registry --publish published=5000,target=5000 registry:2

curl -L https://downloads.portainer.io/portainer-agent-stack.yml -o /tmp/portainer-agent-stack.yml
sudo docker stack deploy --compose-file=/tmp/portainer-agent-stack.yml portainer
"""
TEMPLATE_SCRIPT = """
# import the downloaded disk to local-lvm storage
qm importdisk 9000 bionic-server-cloudimg-amd64.img local-lvm

# finally attach the new disk to the VM as scsi drive
qm set 9000 --scsihw virtio-scsi-pci --scsi0 local-lvm:vm-9000-disk-1
"""