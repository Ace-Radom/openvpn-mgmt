#!/bin/bash

if ! dpkg -s python3-venv > /dev/null 2>&1; then
    echo "Please intall python3-venv pkg first"
    exit 1
fi

cd /opt
python3 -m venv glances
cd ./glances
./bin/pip install glances[web]

echo "glances has been installed successfully"
