#!/bin/bash

set -e

echo "Installing nvm and npm"
if [ ! -d "$HOME/.nvm" ]; then
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash
    export NVM_DIR="$HOME/.nvm"
    # This loads nvm
    # shellcheck source=/dev/null
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  
    [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
else
    echo "NVM is already installed."
fi

echo "Installing dependencies"
python -m venv .venv 
source .venv/bin/activate
python -m pip install --upgrade pip
pip install setuptools wheel
pip install -r requirements.txt


# Setup script to launch validator and configure the dashboard

# Function to check if a command exists
command_exists() {
    echo "Checking if $1 exists..."
    command -v "$1" >/dev/null 2>&1
}

echo "Checking for required tools"
# Check for required tools
for cmd in jq comx; do
    if ! command_exists "$cmd"; then
        echo "Error: $cmd is not installed. Please install it and try again."
        exit 1
    fi
done

echo "Checking for .env file"
# Create .env file if it doesn't existtouch .env

# Function to add or update .env entries
update_env() {
    if grep -q "^$1=" .env; then
        sed -i "s|^$1=.*|$1=$2|" .env
    else
        echo "$1=$2" >> .env
    fi
}

# Miner data path
echo "Miner data path (y/n)?"
read -p "(default: data/instance_data/miner.json) " MINER_PATH

if [[ "$MINER_PATH" =~ ^[Yy](es)?$ ]] || [ -z "$MINER_PATH" ]; then
    MINER_PATH="data/instance_data/miner.json"
fi

update_env "MINER_PATH" "$MINER_PATH"

# Validator Name
echo "Validator Name (string)?"
read -p "(default: eden.Validator_1) " VALIDATOR_NAME

VALIDATOR_NAME=${VALIDATOR_NAME:-eden.Validator_1}

update_env "VALIDATOR_NAME" "$VALIDATOR_NAME"

echo "Creating key: $VALIDATOR_NAME"

if ! OUTPUT=$(comx key create "$VALIDATOR_NAME"); then
    echo "Error creating key. Exiting."
    exit 1
fi

echo "$OUTPUT"

KEY_PATH="$HOME/.commune/key/$VALIDATOR_NAME.json"

if [ ! -f "$KEY_PATH" ]; then
    echo "Error: Key file not found at $KEY_PATH"
    exit 1
fi

JSON_STRING=$(cat "$KEY_PATH")
STRING=$(echo "$JSON_STRING" | jq -r ".data")
JSON=$(echo "$STRING" | jq ".")

VALIDATOR_SS58_KEY=$(echo "$JSON" | jq -r .ss58_address)

update_env "VALIDATOR_SS58_KEY" "$VALIDATOR_SS58_KEY"

echo "Setting private key"

PRIVATE_KEY=$(echo "$JSON" | jq -r .private_key)
update_env "VALIDATOR_PRIVATE_KEY" "$PRIVATE_KEY"

# Print the contents of .env for verification
echo "Contents of .env file:"
cat .env
echo "Creating Query Maps"

# Create directories
mkdir -p data/querymaps data/instance_data

# Create JSON files
declare -A json_files=(
    ["data/querymaps/time.json"]="{}"
    ["data/instance_data/miners.json"]="{}"
    ["data/instance_data/validator.json"]="{}"
    ["data/instance_data/key_data.json"]="{}"
    ["data/instance_data/track_balance.json"]="{}"
)

for file in "${!json_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "${json_files[$file]}" > "$file"
    fi
done

# Create a new script to run in the activated environment
cat << EOF > run_validator.sh
#!/bin/bash

set -e

# Ensure nvm is available
export NVM_DIR="\$HOME/.nvm"
[ -s "\$NVM_DIR/nvm.sh" ] && \. "\$NVM_DIR/nvm.sh"

nvm use 20
npm install -g npm@latest
npm install pm2 -g

# Activate virtual environment
source .venv/bin/activate

python3 -m pip install --upgrade pip
pip install setuptools wheel
pip install -r requirements.txt

COMX_PATH=\$(command -v comx)
BIN_PATH=\$(dirname "\$COMX_PATH")
VENV_PATH=\$(dirname "\$BIN_PATH")

# Use find to locate cli.py, which is more flexible
COMMUNE_CODE_PATH=\$(find "\$VENV_PATH" -name cli.py | grep communex)

if [ -z "\$COMMUNE_CODE_PATH" ]; then
    echo "Error: Unable to find cli.py in the virtual environment."
    exit 1
fi

update_env "CODE_PATH" "\$COMMUNE_CODE_PATH"

echo "Running query_loop.py"

if command_exists pm2; then
    pm2 start "python query_loop.py"
else
    echo "Error: PM2 is not installed or not in PATH. Please check the installation."
    exit 1
fi

echo "Done"
EOF

chmod +x run_validator.sh

echo "Setup complete. To run the validator, execute: source run_validator.sh"