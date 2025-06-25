"""
Example usage of the task-to-code pipeline.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def example_jira_processing():
    """Example of processing a JIRA issue."""
    from src.pipeline import TaskToCodePipeline
    
    try:
        # Initialize pipeline
        pipeline = TaskToCodePipeline('config.yaml')
        
        # Process a JIRA issue
        issue_key = "PROJ-123"  # Replace with your actual issue key
        result = pipeline.process_jira_task(issue_key)
        
        print(f"✅ Successfully processed {issue_key}")
        print(f"Generated {len(result['generated_files'])} files")
        
        # Show generated files
        for file_info in result['generated_files']:
            print(f"  - {file_info['type']}: {file_info['original_path']}")
        
        # Show dependencies
        if result['dependencies']:
            print("\n📦 New dependencies:")
            for dep in result['dependencies']:
                print(f"  - {dep}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def example_code_update():
    """Example of updating existing code."""
    from src.pipeline import TaskToCodePipeline
    
    try:
        pipeline = TaskToCodePipeline('config.yaml')
        
        # Update existing code
        file_path = "src/example.py"  # Replace with your file
        requirements = "Add input validation and error handling"
        
        result = pipeline.update_existing_code(file_path, requirements)
        
        print(f"✅ Successfully updated {file_path}")
        if result['backup_path']:
            print(f"Backup: {result['backup_path']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def example_project_analysis():
    """Example of analyzing project structure."""
    from src.project_analyzer import ProjectAnalyzer
    
    try:
        # Analyze current directory as an example
        analyzer = ProjectAnalyzer(".")
        
        # Get project structure
        structure = analyzer.get_project_structure()
        
        print("📊 Project Analysis:")
        print(f"  - Total files: {structure['total_files']}")
        print(f"  - Total directories: {structure['total_directories']}")
        print(f"  - Languages: {', '.join(structure['languages'])}")
        print(f"  - Frameworks: {', '.join(structure['frameworks'])}")
        
        # Get context summary
        context = analyzer.get_context_summary()
        
        print("\n📁 Important files found:")
        for file_info in context['important_files'][:5]:  # Show first 5
            print(f"  - {file_info['path']} ({file_info['size']} bytes)")
        
        return structure
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def example_confluence_processing():
    """Example of processing a Confluence page."""
    from src.pipeline import TaskToCodePipeline
    
    try:
        pipeline = TaskToCodePipeline('config.yaml')
        
        # Process a Confluence page
        page_id = "123456789"  # Replace with your page ID
        result = pipeline.process_confluence_page(page_id)
        
        print(f"✅ Successfully processed Confluence page {page_id}")
        print(f"Generated {len(result['generated_files'])} files")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    """Run examples based on command line argument."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Task-to-Code Pipeline Examples")
    parser.add_argument(
        'example',
        choices=['jira', 'confluence', 'update', 'analyze'],
        help='Which example to run'
    )
    
    args = parser.parse_args()
    
    print(f"🔧 Running {args.example} example...\n")
    
    if args.example == 'jira':
        example_jira_processing()
    elif args.example == 'confluence':
        example_confluence_processing() 
    elif args.example == 'update':
        example_code_update()
    elif args.example == 'analyze':
        example_project_analysis()


if __name__ == "__main__":
    main()
