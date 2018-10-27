#!/usr/bin/env bash

set -e

if [ -z "$1" ]; then
    echo "Please provide a remote server to rsync to"
    exit 1
fi
REMOTE_SERVER=$1

# To check that it will build properly
$(aws ecr get-login --profile sixthman-shraybansal | sed 's/-e none//g') &
docker build -t 146006631841.dkr.ecr.us-west-1.amazonaws.com/flask-espn-dashboard:latest .
docker push 146006631841.dkr.ecr.us-west-1.amazonaws.com/flask-espn-dashboard:latest

# rsync -azvh ../espn-dashboard $REMOTE_SERVER:espn-dashboard # Only use to instantiate
rsync -azvh docker-compose-espn-dashboard.yml $REMOTE_SERVER:espn-dashboard/docker-compose-espn-dashboard.yml

ssh $REMOTE_SERVER << EOF
    cd espn-dashboard
    docker-compose -f docker-compose-espn-dashboard.yml down
    docker-compose rm -f espn-dashboard-webserver
    docker rmi -f 146006631841.dkr.ecr.us-west-1.amazonaws.com/flask-espn-dashboard:latest
    docker-compose -f docker-compose-espn-dashboard.yml up -d
EOF