#!/bin/bash
# ESC
# create virtual environment and start ESC

echo "Activating virtual environment..."
if [ -n "$VIRTUAL_ENV" ]; then
    pip install .[dev]
else
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
    pip install .[dev]
fi

echo "Virtual environment successfully updated!"