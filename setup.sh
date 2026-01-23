#!/bin/bash
set -e

echo "Setting up Personal LLM..."

# Create venv
python3 -m venv venv
source venv/bin/activate

# Install deps
pip install -r requirements.txt

# Create config if doesn't exist
if [ ! -f config.toml ]; then
	cp config.toml.example config.toml
	echo "Created config.toml - please edit it with your settings"
fi

echo "Setup complete! Run: source venv/bin/activate && cd src && python main.py"
