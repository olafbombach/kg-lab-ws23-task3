#!/bin/bash
# ESC
# create virtual environment and start ESC

git pull

# Check if python command is available
if ! command -v python &>/dev/null; then
    echo "Python is not installed. Please install Python and try again."
    exit 1
fi
echo "Found Python in commands..."

# Create a virtual environment
if [ -d "venv" ]; then
    echo "Virtual Environment already exists..."
else
    python -m venv venv
    echo "Virtual Environment initialized"
fi

# Activate the virtual environment based on the operating system
echo "Activating virtual environment..."
case "$(uname -s)" in
    Linux*) 
    echo "Linux system detected. Using Bash activation script."    
    source "venv/bin/activate" ;;
    Darwin*)    
    echo "Mac system detected. Using Bash activation script."
    source "venv/bin/activate" ;;
    CYGWIN*|MINGW*|MSYS*)
    echo "Windows system detected. Using Windows activation script." 
    source "venv\Scripts\activate" ||. "venv\Scripts\activate" ;;
    *)          
    echo "Unsupported operating system. Please activate the virtual environment manually." ;;
esac

# Check if virtual environment is activated (used for decoding)
if [[ $VIRTUAL_ENV == "" ]]; then
    echo "Failed to activate the virtual environment. Please activate it manually."
    exit 1
fi

# Install dependencies from pyproject.toml using pip
echo "Installing dependencies..."
pip install .

echo "Setup complete!"
esc -h
