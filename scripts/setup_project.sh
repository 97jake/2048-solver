#!/bin/bash

# Install pyenv if not already installed
if ! command -v pyenv &> /dev/null; then
    echo "Installing pyenv..."
    curl https://pyenv.run | bash
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init --path)"
fi

# Read Python version from .python-version file or set to default
if [ -f .python-version ]; then
    python_version=$(cat .python-version)
else
    echo "Warning: .python-version file not found. Setting Python version to 3.11.3."
    python_version="3.11.3"
fi

# Install required Python version
echo "Installing Python version $python_version..."
pyenv install -s "$python_version"

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

pyenv global "$python_version"
export PATH="$HOME/.pyenv/versions/$python_version/bin:$PATH"
echo "Using Python version $(python --version) from $(which python)"

# Install project dependencies
echo "Installing project dependencies..."
pip install -r requirements.txt

echo "Setup complete. You can now start using the project!"

