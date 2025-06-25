#!/bin/bash

# Activation script for task-to-code virtual environment
# Usage: source activate_env.sh

if [ -d "venv" ]; then
    echo "🚀 Activating task-to-code virtual environment..."
    source venv/bin/activate
    echo "✅ Virtual environment activated!"
    echo ""
    echo "📋 Available commands:"
    echo "  python main.py jira ISSUE-KEY     # Process JIRA issue"
    echo "  python main.py confluence PAGE-ID # Process Confluence page"
    echo "  python main.py update FILE REQS   # Update existing code"
    echo "  python main.py test               # Get test instructions"
    echo "  python validate.py                # Validate setup"
    echo "  python examples.py analyze        # Analyze project structure"
    echo ""
    echo "🚀 Alternative: Use the wrapper script (auto-activates env):"
    echo "  ./task-to-code.sh jira ISSUE-KEY  # No need to activate manually"
    echo ""
    echo "📚 Documentation:"
    echo "  cat README.md                     # Main documentation"
    echo "  cat WORKFLOW.md                   # Detailed workflow"
    echo ""
    echo "🔧 To deactivate: deactivate"
else
    echo "❌ Virtual environment not found!"
    echo "💡 Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
fi
