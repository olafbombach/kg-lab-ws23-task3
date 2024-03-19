#!/bin/bash
# ESC
# run the tests

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

# Search for green package
echo "Search for pytest in venv..."
pip list | egrep "^pytest " 
if [ $? -ne 0 ]
then
  pip install .[test]
fi

# Apply test
pytest