#!/bin/bash
# ESC
# create virtual environment and start ESC
python3_installed=false

git pull

# Check if python ot python3 command is available
if command -v python &>/dev/null; then
    echo "Found Python as command..."
elif command -v python3 &>/dev/null; then
    echo "Found Python3 as command..."
    python3_installed=true
else
    echo "Python is not installed. Please install Python and try again."
    exit 1
fi

# Create a virtual environment
if [ -d "venv" ]; then
    echo "Virtual Environment already exists..."
else
    # Create virtual environment based on python version
    if [ "$python3_installed" = true ]; then
        python3 -m venv venv
    else
        python -m venv venv
    fi
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
