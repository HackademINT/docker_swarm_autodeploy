#!/bin/bash

i=1
VM_ID="100$i"
VM_IP="10.33.0.1$i"
if [ "$(qm list | grep $VM_ID | wc -l)" -eq 0 ]; then
	qm clone 9000 $VM_ID \
		--name "docker$i" \
		--description 'Docker $i VM created by bonnetn' \
		--pool dockerswarm 
	qm set $VM_ID --net0 model=virtio,bridge=vmbr1337
	qm set $VM_ID --ipconfig0 ip=${VM_IP}/16,gw=10.33.0.1
	qm set $VM_ID --nameserver '157.159.10.12'
	qm set $VM_ID --ciuser deploy
	qm set $VM_ID --sshkey ~/.ssh/id_rsa.pub
	qm set $VM_ID --agent 1
	qm set $VM_ID --autostart 1
	qm start $VM_ID
fi

read -p "Press enter to continue when the VM is started"

scp -o StrictHostKeyChecking=no .provision_vm.sh deploy@${VM_IP}:./provision.sh
ssh -o StrictHostKeyChecking=no deploy@$VM_IP bash provision.sh
ssh -o StrictHostKeyChecking=no deploy@$VM_IP "sudo docker swarm init --advertise-addr $VM_IP" > join_cluster.cmd
cat join_cluster.cmd | head -n 5 | tail -n 1 | tee join_cluster.sh

for i in {2..5}; do
	VM_ID="100$i"
	VM_IP="10.33.0.1$i"
	if [ "$(qm list | grep $VM_ID | wc -l)" -eq 0 ]; then
		qm clone 9000 $VM_ID \
			--name "docker$i" \
			--description 'Docker $i VM created by bonnetn' \
			--pool dockerswarm 
		qm set $VM_ID --net0 model=virtio,bridge=vmbr1337
		qm set $VM_ID --ipconfig0 ip=${VM_IP}/16,gw=10.33.0.1
		qm set $VM_ID --nameserver '157.159.10.12'
		qm set $VM_ID --ciuser deploy
		qm set $VM_ID --sshkey ~/.ssh/id_rsa.pub
		qm set $VM_ID --agent 1
                qm set $VM_ID --autostart 1
		qm start $VM_ID
	fi
done

read -p "Press enter to continue when the worker VMs are started"

for i in {2..5}; do
	VM_IP="10.33.0.1$i"
	scp -o StrictHostKeyChecking=no .provision_vm.sh deploy@${VM_IP}:./provision.sh
	ssh -o StrictHostKeyChecking=no deploy@$VM_IP bash provision.sh
	scp -o StrictHostKeyChecking=no join_cluster.sh deploy@${VM_IP}:./
	ssh -o StrictHostKeyChecking=no deploy@$VM_IP sudo bash join_cluster.sh
done

VM_IP="10.33.0.11"
scp -o StrictHostKeyChecking=no .promote_everyone.sh deploy@${VM_IP}:./promote.sh
ssh -o StrictHostKeyChecking=no deploy@$VM_IP sudo bash promote.sh

