#!/bin/bash

# Wrapper script for task-to-code that automatically activates the virtual environment
# Usage: ./task-to-code.sh [arguments]

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "💡 Please run the setup first:"
    echo "   cd $SCRIPT_DIR"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment and run main.py
cd "$SCRIPT_DIR"
source venv/bin/activate
python main.py "$@"
