#!/bin/bash
set -e

echo "Checking Docker socket permissions..."

if [ -S /var/run/docker.sock ]; then
    echo "Fixing permissions for Docker socket..."
    sudo chmod 666 /var/run/docker.sock
else
    echo "Warning: Docker socket not found!"
fi

# Start Jenkins as usual
exec /usr/bin/tini -- /usr/local/bin/jenkins.sh
