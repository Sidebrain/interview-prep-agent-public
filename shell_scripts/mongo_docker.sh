#!/usr/bin/env bash

docker pull mongodb/mongodb-community-server:latest
docker run \
  --name mongodb \
  -p 27017:27017 \
  -d \
  -v mongodb_data:/data/db \
  mongodb/mongodb-community-server:latest
