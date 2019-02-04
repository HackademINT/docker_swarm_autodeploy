#!/bin/bash
docker node ls | awk 'NR>1 {print $1}' | xargs docker node promote

docker service create --name registry --publish published=5000,target=5000 registry:2

