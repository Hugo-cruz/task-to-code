#!/bin/bash

# Installation script for task-to-code pipeline

echo "🚀 Setting up Task-to-Code Pipeline..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

echo "✅ Python 3 found"

# Create virtual environment (recommended)
read -p "🤔 Create a virtual environment? (recommended) [y/N]: " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
    
    echo "✅ Virtual environment created and activated"
    echo "💡 To activate in the future, run: source venv/bin/activate"
fi

# Install dependencies
echo "📥 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Setup configuration
echo "⚙️  Setting up configuration..."
python3 main.py setup

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit config.yaml with your API credentials"
echo "2. Set your project repository path"
echo "3. Run your first task: python3 main.py jira YOUR-ISSUE-KEY"
echo ""
echo "For help: python3 main.py --help"
