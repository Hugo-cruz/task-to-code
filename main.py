#!/usr/bin/env python3
"""
Command-line interface for the task-to-code pipeline.
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Check if we're in the right environment and provide helpful error messages
try:
    from src.pipeline import TaskToCodePipeline
except ImportError as e:
    print("❌ Import Error: Required dependencies not found.")
    print(f"   Details: {e}")
    print()
    print("💡 This usually means the virtual environment is not activated.")
    print("   Please run one of the following:")
    print()
    print("   Option 1: Activate virtual environment manually")
    print("   source venv/bin/activate")
    print("   python main.py [command]")
    print()
    print("   Option 2: Use the activation script")
    print("   source activate_env.sh")
    print("   python main.py [command]")
    print()
    print("   Option 3: Install dependencies globally (not recommended)")
    print("   pip install -r requirements.txt")
    print()
    print("📚 For more help, see README.md or run: python validate.py")
    sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Task-to-Code Pipeline - Generate code from Confluence/JIRA tasks"
    )
    
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # JIRA command
    jira_parser = subparsers.add_parser('jira', help='Process a JIRA issue')
    jira_parser.add_argument('issue_key', help='JIRA issue key (e.g., PROJ-123)')
    
    # Confluence command
    confluence_parser = subparsers.add_parser('confluence', help='Process a Confluence page')
    confluence_parser.add_argument('page_id', help='Confluence page ID')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update existing code')
    update_parser.add_argument('file_path', help='Path to file to update (relative to project root)')
    update_parser.add_argument('requirements', help='New requirements or changes needed')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run tests')
    test_parser.add_argument('--pattern', help='Test pattern to filter by')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup configuration')
    
    args = parser.parse_args()
    
    if args.command == 'setup':
        setup_config()
        return
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        pipeline = TaskToCodePipeline(args.config)
        
        if args.command == 'jira':
            result = pipeline.process_jira_task(args.issue_key)
            print(f"\n✅ Successfully processed JIRA issue: {args.issue_key}")
            print(f"Generated {len(result['generated_files'])} files")
            if result['dependencies']:
                print(f"\n📦 Dependencies to install:")
                for dep in result['dependencies']:
                    print(f"  - {dep}")
        
        elif args.command == 'confluence':
            result = pipeline.process_confluence_page(args.page_id)
            print(f"\n✅ Successfully processed Confluence page: {args.page_id}")
            print(f"Generated {len(result['generated_files'])} files")
        
        elif args.command == 'update':
            result = pipeline.update_existing_code(args.file_path, args.requirements)
            print(f"\n✅ Successfully updated: {args.file_path}")
            if result['backup_path']:
                print(f"Backup created: {result['backup_path']}")
        
        elif args.command == 'test':
            result = pipeline.run_tests(args.pattern)
            print(f"\n🧪 Test Instructions:")
            print(result['instructions'])
    
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        if "config.yaml" in str(e):
            print("\n💡 Tip: Run 'python main.py setup' to create a configuration file")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def setup_config():
    """Setup configuration file."""
    config_path = Path('config.yaml')
    template_path = Path('config.template.yaml')
    
    if config_path.exists():
        response = input(f"Configuration file already exists at {config_path}. Override? (y/N): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    if not template_path.exists():
        print(f"❌ Template file not found: {template_path}")
        print("Please ensure config.template.yaml exists in the current directory.")
        return
    
    # Copy template to config
    import shutil
    shutil.copy2(template_path, config_path)
    
    print(f"✅ Configuration file created: {config_path}")
    print("\n📝 Please edit the configuration file and fill in your values:")
    print(f"   - Confluence/JIRA API credentials")
    print(f"   - Project repository path")
    print(f"   - Anthropic API key")
    print(f"\n💡 Tip: You can get an Atlassian API token from:")
    print(f"   https://id.atlassian.com/manage-profile/security/api-tokens")


if __name__ == "__main__":
    main()
