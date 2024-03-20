#!/bin/bash
# ESC
# automatically download / update necessary resources

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

# get data
esc resources