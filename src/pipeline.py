"""Main pipeline orchestrator for the task-to-code application."""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from .config import Config
from .confluence_client import ConfluenceJiraClient
from .project_analyzer import ProjectAnalyzer
from .claude_generator import ClaudeCodeGenerator


class TaskToCodePipeline:
    """Main pipeline that orchestrates the task-to-code process."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the pipeline with configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = Config(config_path)
        
        # Initialize clients
        confluence_config = self.config.confluence_config
        self.confluence_client = ConfluenceJiraClient(
            base_url=confluence_config['base_url'],
            username=confluence_config['username'],
            api_token=confluence_config['api_token']
        )
        
        project_config = self.config.project_config
        self.project_analyzer = ProjectAnalyzer(
            repository_path=project_config['repository_path'],
            exclude_patterns=project_config.get('exclude_patterns', [])
        )
        
        anthropic_config = self.config.anthropic_config
        self.code_generator = ClaudeCodeGenerator(
            api_key=anthropic_config['api_key'],
            model=anthropic_config.get('model', 'claude-3-5-sonnet-20241022'),
            max_tokens=anthropic_config.get('max_tokens', 4000)
        )
        
        # Setup output directories
        self.output_config = self.config.output_config
        self._setup_output_directories()
    
    def process_jira_task(self, issue_key: str) -> Dict[str, Any]:
        """
        Process a JIRA task through the complete pipeline.
        
        Args:
            issue_key: JIRA issue key (e.g., 'PROJ-123')
            
        Returns:
            Dictionary with processing results
        """
        print(f"Processing JIRA task: {issue_key}")
        
        # Step 1: Extract task data
        print("1. Extracting task data from JIRA...")
        task_data = self.confluence_client.get_jira_issue_details(issue_key)
        
        # Step 2: Analyze project structure
        print("2. Analyzing project structure...")
        project_context = self.project_analyzer.get_context_summary()
        
        # Step 3: Generate code
        print("3. Generating code with Claude AI...")
        code_result = self.code_generator.generate_code_from_task(task_data, project_context)
        
        # Step 4: Generate tests
        print("4. Generating tests...")
        test_result = self.code_generator.generate_tests(code_result['files'], project_context)
        
        # Step 5: Save generated files
        print("5. Saving generated files...")
        saved_files = self._save_generated_files(code_result, test_result, issue_key)
        
        # Step 6: Create summary report
        result = {
            'issue_key': issue_key,
            'task_data': task_data,
            'generated_files': saved_files,
            'analysis': code_result.get('analysis', ''),
            'notes': code_result.get('notes', ''),
            'dependencies': code_result.get('dependencies', []) + test_result.get('dependencies', []),
            'test_strategy': test_result.get('strategy', ''),
            'run_instructions': test_result.get('run_instructions', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        # Save summary
        self._save_summary_report(result)
        
        print(f"✅ Task processing completed! Check the output directory: {self.output_config.get('generated_code_path', './generated')}")
        return result
    
    def process_confluence_page(self, page_id: str) -> Dict[str, Any]:
        """
        Process a Confluence page through the pipeline.
        
        Args:
            page_id: Confluence page ID
            
        Returns:
            Dictionary with processing results
        """
        print(f"Processing Confluence page: {page_id}")
        
        # Step 1: Extract page content
        print("1. Extracting content from Confluence...")
        page_data = self.confluence_client.get_confluence_page(page_id)
        content = self.confluence_client.get_confluence_page_content(page_id)
        
        # Transform to task-like format
        task_data = {
            'key': f"CONF-{page_id}",
            'summary': page_data.get('title', 'Confluence Page'),
            'description': content,
            'issue_type': 'Story',
            'priority': 'Medium',
            'status': 'To Do',
            'labels': [],
            'components': [],
            'acceptance_criteria': self._extract_requirements_from_content(content)
        }
        
        # Continue with normal pipeline
        return self._process_task_data(task_data)
    
    def update_existing_code(self, file_path: str, new_requirements: str) -> Dict[str, Any]:
        """
        Update existing code based on new requirements.
        
        Args:
            file_path: Path to the existing code file
            new_requirements: New requirements or changes needed
            
        Returns:
            Dictionary with update results
        """
        print(f"Updating existing code: {file_path}")
        
        # Read existing code
        try:
            existing_code = self.project_analyzer.get_file_content(file_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get project context
        project_context = self.project_analyzer.get_context_summary()
        
        # Generate updated code
        updated_code = self.code_generator.review_and_update_code(
            existing_code, new_requirements, project_context
        )
        
        # Backup existing file
        if self.output_config.get('backup_existing', True):
            backup_path = self._create_backup(file_path)
            print(f"Backup created: {backup_path}")
        
        # Save updated code
        full_path = Path(self.config.project_config['repository_path']) / file_path
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(updated_code)
        
        result = {
            'file_path': file_path,
            'backup_path': backup_path if self.output_config.get('backup_existing', True) else None,
            'updated_code': updated_code,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"✅ Code updated successfully!")
        return result
    
    def run_tests(self, test_pattern: Optional[str] = None) -> Dict[str, Any]:
        """
        Run tests in the project.
        
        Args:
            test_pattern: Optional pattern to filter tests
            
        Returns:
            Dictionary with test results
        """
        print("Running tests...")
        
        # This would typically run pytest, jest, or other test runners
        # For now, provide instructions
        project_languages = self.project_analyzer._detect_languages()
        
        if 'Python' in project_languages:
            test_command = "pytest"
            if test_pattern:
                test_command += f" -k {test_pattern}"
        elif 'JavaScript' in project_languages or 'TypeScript' in project_languages:
            test_command = "npm test"
        else:
            test_command = "# Please run your project's test command"
        
        return {
            'test_command': test_command,
            'instructions': f"Run the following command in your project directory:\n{test_command}",
            'timestamp': datetime.now().isoformat()
        }
    
    def _process_task_data(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process task data through the pipeline."""
        # Analyze project structure
        print("2. Analyzing project structure...")
        project_context = self.project_analyzer.get_context_summary()
        
        # Generate code
        print("3. Generating code with Claude AI...")
        code_result = self.code_generator.generate_code_from_task(task_data, project_context)
        
        # Generate tests
        print("4. Generating tests...")
        test_result = self.code_generator.generate_tests(code_result['files'], project_context)
        
        # Save generated files
        print("5. Saving generated files...")
        saved_files = self._save_generated_files(code_result, test_result, task_data['key'])
        
        # Create summary report
        result = {
            'issue_key': task_data['key'],
            'task_data': task_data,
            'generated_files': saved_files,
            'analysis': code_result.get('analysis', ''),
            'notes': code_result.get('notes', ''),
            'dependencies': code_result.get('dependencies', []) + test_result.get('dependencies', []),
            'test_strategy': test_result.get('strategy', ''),
            'run_instructions': test_result.get('run_instructions', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        # Save summary
        self._save_summary_report(result)
        
        print(f"✅ Task processing completed!")
        return result
    
    def _setup_output_directories(self):
        """Setup output directories."""
        code_path = Path(self.output_config.get('generated_code_path', './generated'))
        test_path = Path(self.output_config.get('test_path', './tests'))
        
        code_path.mkdir(parents=True, exist_ok=True)
        test_path.mkdir(parents=True, exist_ok=True)
    
    def _save_generated_files(self, code_result: Dict[str, Any], test_result: Dict[str, Any], issue_key: str) -> List[Dict[str, str]]:
        """Save generated files to the output directory."""
        saved_files = []
        
        # Create issue-specific directory
        issue_dir = Path(self.output_config.get('generated_code_path', './generated')) / issue_key
        issue_dir.mkdir(parents=True, exist_ok=True)
        
        # Save code files
        for file_info in code_result.get('files', []):
            file_path = issue_dir / 'code' / file_info['path']
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_info['content'])
            
            saved_files.append({
                'type': 'code',
                'original_path': file_info['path'],
                'saved_path': str(file_path),
                'language': file_info.get('language', 'text')
            })
        
        # Save test files
        for file_info in test_result.get('test_files', []):
            file_path = issue_dir / 'tests' / file_info['path']
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_info['content'])
            
            saved_files.append({
                'type': 'test',
                'original_path': file_info['path'],
                'saved_path': str(file_path),
                'language': file_info.get('language', 'text')
            })
        
        return saved_files
    
    def _save_summary_report(self, result: Dict[str, Any]):
        """Save a summary report of the processing."""
        issue_key = result['issue_key']
        report_path = Path(self.output_config.get('generated_code_path', './generated')) / issue_key / 'summary.json'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # Also create a markdown report
        md_path = report_path.with_suffix('.md')
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(self._create_markdown_report(result))
    
    def _create_markdown_report(self, result: Dict[str, Any]) -> str:
        """Create a markdown report from the results."""
        task_data = result['task_data']
        
        report = f"""# Task Processing Report: {result['issue_key']}

**Generated on:** {result['timestamp']}

## Task Information
- **Title:** {task_data.get('summary', 'N/A')}
- **Type:** {task_data.get('issue_type', 'N/A')}
- **Priority:** {task_data.get('priority', 'N/A')}
- **Status:** {task_data.get('status', 'N/A')}

## Description
{task_data.get('description', 'No description available')}

## Acceptance Criteria
"""
        
        for criteria in task_data.get('acceptance_criteria', []):
            report += f"- {criteria}\n"
        
        report += f"""
## Analysis
{result.get('analysis', 'No analysis available')}

## Generated Files
"""
        
        for file_info in result.get('generated_files', []):
            report += f"- **{file_info['type'].title()}:** `{file_info['original_path']}` → `{file_info['saved_path']}`\n"
        
        report += f"""
## Dependencies
"""
        for dep in result.get('dependencies', []):
            report += f"- {dep}\n"
        
        report += f"""
## Test Strategy
{result.get('test_strategy', 'No test strategy available')}

## Running Tests
{result.get('run_instructions', 'No instructions available')}

## Implementation Notes
{result.get('notes', 'No additional notes')}
"""
        
        return report
    
    def _extract_requirements_from_content(self, content: str) -> List[str]:
        """Extract requirements from Confluence page content."""
        requirements = []
        lines = content.split('\n')
        
        in_requirements = False
        for line in lines:
            line = line.strip()
            
            if any(keyword in line.lower() for keyword in ['requirements', 'acceptance criteria', 'should', 'must']):
                in_requirements = True
                continue
            
            if in_requirements:
                if line.startswith(('-', '*', '•')) or line[0:2].replace('.', '').isdigit():
                    requirements.append(line.lstrip('- *•0123456789. '))
                elif line and not any(c.isalnum() for c in line):
                    break  # End of requirements section
        
        return requirements
    
    def _create_backup(self, file_path: str) -> str:
        """Create a backup of an existing file."""
        full_path = Path(self.config.project_config['repository_path']) / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"Cannot backup non-existent file: {file_path}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = full_path.with_suffix(f".backup_{timestamp}{full_path.suffix}")
        
        shutil.copy2(full_path, backup_path)
        return str(backup_path)
