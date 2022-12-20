#!/bin/bash

# from https://gist.github.com/Maxzor/6a3ca2c5c1c28af583711abc8e5fda01

# Stop and remove all containers
echo -e "Removing containers\n"
if [ -n "$(docker container ls -aq)" ]; then
  docker container stop $(docker container ls -aq);
  docker container rm $(docker container ls -aq);
fi;

# Remove all images
echo -e "Removing images\n"
if [ -n "$(docker images -aq)" ]; then
  docker rmi -f $(docker images -aq);
fi;

# Remove all volumes
echo -e "Removing volumes\n"
if [ -n "$(docker volume ls -q)" ]; then
  docker volume rm $(docker volume ls -q);
fi;

# Remove all networks except defaults: bridge, host, none
echo -e "Removing networks\n"
if [ -n "$(docker network ls | awk '{print $1" "$2}' | grep -v 'ID\|bridge\|host\|none' | awk '{print $1}')" ]; then
  docker network rm $(docker network ls | awk '{print $1" "$2}' | grep -v 'ID\|bridge\|host\|none' | awk '{print $1}');
fi;

# Your installation should now be all fresh and clean.

# The following commands should not output any items:
# docker ps -a
# docker images -a 
# docker volume ls

# The following command should only show the default networks:
# docker network ls
