# Docker Swarm autodeploy

This script automatically deploys a Docker Swarm cluster on our infra.

Once this is done, you can create docker services. 
In other words you can take your docker-compose.yml and "transform" it into a persistent service.

## TLDR
```sh
ssh deploy@10.20.20.11

# Get information about services...
sudo docker stack ls
sudo docker service ls # See all the services running on the cluster...

git clone https://my_awesome_service
cd my_awesome_service

sudo docker-compose build
sudo docker-compose push
sudo docker stack deploy NAME_OF_YOUR_SERVICE --compose-file docker-compose.yml

```

## I want to deploy a new service / I want to update a service!

### Tasks:
* Build the service
* Push the service to our registry
* Deploy the service

### Building and pushing the service...
In order for the containers to be available to all of the VM running *Docker*, you __must__ specify a registry server of the cluster in your *docker-swarm.yml*. 

The registry will store the built version of your containers.

First, if you build some custom containers in your dockerfile, for instance: 
```yaml
version: '3'
services:
  api:
    build: ./api
    environment:
      MY_ENV_VAR: 5000
[...]
```


Add a "**image:**" directive for each **build:**.
```yaml
version: '3'
services:
  api:
    build: ./api
    image: localhost:5000/rootme_api_python
    environment:
      MY_ENV_VAR: 5000
[...]
```

Then you will build your service.

SSH on docker1:
```sh
ssh deploy@10.20.20.11

# Transfer your project on the VM... (you can use git, wget, scp...)
git clone https://my_awesome_service
cd my_awesome_service
```

#### 1/ Build your service
```sh
sudo docker-compose build
```

#### 2/ Push your service on the registry
```sh
sudo docker-compose push
```

#### 3/ Deploy your service
```sh
sudo docker stack deploy NAME_OF_YOUR_SERVICE --compose-file docker-compose.yml
sudo docker stack ls
sudo docker service ls # See all the services running on the cluster...
```
