#!/bin/bash
# ESC
# start GUI and solve unclear states manually

# Activating venv
echo "Activating virtual environment..."
if [ -n "$VIRTUAL_ENV" ]; then
    echo "Venv already acitvated..."
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
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "Venv acitvated..."
    fi
fi

esc solve