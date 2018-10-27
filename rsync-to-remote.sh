#!/usr/bin/env bash

set -e

if [ -z "$1" ]; then
    echo "Please provide a remote server to rsync to"
    exit 1
fi
REMOTE_SERVER=$1

# To check that it will build properly
docker build -t test-espn-dashboard .

rsync -azvh ../espn-dashboard $REMOTE_SERVER:espn-dashboard # Only use to instantiate
rsync -azvh Dockerfile $REMOTE_SERVER:espn-dashboard/Dockerfile
rsync -azvh src $REMOTE_SERVER:espn-dashboard/src
rsync -azvh docker-compose-espn-dashboard.yml $REMOTE_SERVER:espn-dashboard/docker-compose-espn-dashboard.yml

ssh $REMOTE_SERVER << EOF
    cd espn-dashboard
    docker build -t flask-espn-dashboard .
    docker-compose -f docker-compose-espn-dashboard.yml up -d
EOF