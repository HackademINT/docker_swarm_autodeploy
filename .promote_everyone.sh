#!/bin/bash
docker node ls | awk 'NR>1 {print $1}' | xargs docker node promote
