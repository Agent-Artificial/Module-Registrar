#!/bin/bash

set -e

# Ensure nvm is available
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

nvm use 20
npm install -g npm@latest
npm install pm2 -g

# Activate virtual environment
source .venv/bin/activate

python3 -m pip install --upgrade pip
pip install setuptools wheel
pip install -r requirements.txt

COMX_PATH=$(command -v comx)
BIN_PATH=$(dirname "$COMX_PATH")
VENV_PATH=$(dirname "$BIN_PATH")

# Use find to locate cli.py, which is more flexible
COMMUNE_CODE_PATH=$(find "$VENV_PATH" -name cli.py | grep communex)

if [ -z "$COMMUNE_CODE_PATH" ]; then
    echo "Error: Unable to find cli.py in the virtual environment."
    exit 1
fi

update_env "CODE_PATH" "$COMMUNE_CODE_PATH"

echo "Running query_loop.py"

if command_exists pm2; then
    pm2 start "python query_loop.py"
else
    echo "Error: PM2 is not installed or not in PATH. Please check the installation."
    exit 1
fi

echo "Done"
