"""Claude AI client for code generation using Anthropic's API."""

import anthropic
from typing import Dict, Any, List, Optional
import json


class ClaudeCodeGenerator:
    """Client for generating code using Claude AI."""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022", max_tokens: int = 4000):
        """
        Initialize the Claude client.
        
        Args:
            api_key: Anthropic API key
            model: Claude model to use
            max_tokens: Maximum tokens for responses
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
    
    def generate_code_from_task(self, task_data: Dict[str, Any], project_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate code based on task requirements and project context.
        
        Args:
            task_data: Task information from Confluence/JIRA
            project_context: Project structure and context
            
        Returns:
            Dictionary containing generated code and metadata
        """
        prompt = self._build_code_generation_prompt(task_data, project_context)
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
        )
        
        # Parse the response to extract code files
        content = response.content[0].text
        return self._parse_code_response(content, task_data)
    
    def generate_tests(self, code_files: List[Dict[str, Any]], project_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate unit and integration tests for the provided code.
        
        Args:
            code_files: List of generated code files
            project_context: Project structure and context
            
        Returns:
            Dictionary containing generated test files
        """
        prompt = self._build_test_generation_prompt(code_files, project_context)
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        content = response.content[0].text
        return self._parse_test_response(content)
    
    def review_and_update_code(self, existing_code: str, new_requirements: str, project_context: Dict[str, Any]) -> str:
        """
        Review and update existing code based on new requirements.
        
        Args:
            existing_code: Current code content
            new_requirements: New requirements or changes needed
            project_context: Project structure and context
            
        Returns:
            Updated code content
        """
        prompt = self._build_code_update_prompt(existing_code, new_requirements, project_context)
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        return response.content[0].text
    
    def _build_code_generation_prompt(self, task_data: Dict[str, Any], project_context: Dict[str, Any]) -> str:
        """Build the prompt for code generation."""
        
        prompt = f"""You are an expert software developer. Based on the following task requirements and project context, generate the necessary code files.

TASK INFORMATION:
- Title: {task_data.get('summary', 'N/A')}
- Type: {task_data.get('issue_type', 'N/A')}
- Priority: {task_data.get('priority', 'N/A')}
- Description: {task_data.get('description', 'N/A')}

ACCEPTANCE CRITERIA:
{chr(10).join(f"- {criteria}" for criteria in task_data.get('acceptance_criteria', []))}

PROJECT CONTEXT:
- Languages: {', '.join(project_context['project_overview']['languages'])}
- Frameworks: {', '.join(project_context['project_overview']['frameworks'])}
- Directory Structure:
{self._format_directory_structure(project_context['directory_structure'])}

IMPORTANT FILES CONTEXT:
{self._format_important_files(project_context['important_files'])}

REQUIREMENTS:
1. Generate clean, maintainable code that follows the project's existing patterns
2. Include proper error handling and logging
3. Add comprehensive docstrings and comments
4. Follow the coding standards evident in the existing codebase
5. Create any necessary configuration or setup files
6. Ensure the code integrates well with the existing project structure

Please provide your response in the following format:

## Analysis
[Brief analysis of the requirements and approach]

## Files to Create/Modify

### File: path/to/file.ext
```language
[code content]
```

### File: path/to/another_file.ext
```language
[code content]
```

## Implementation Notes
[Any important notes about the implementation]

## Dependencies
[List any new dependencies that need to be installed]
"""
        
        return prompt
    
    def _build_test_generation_prompt(self, code_files: List[Dict[str, Any]], project_context: Dict[str, Any]) -> str:
        """Build the prompt for test generation."""
        
        code_content = ""
        for file_info in code_files:
            code_content += f"\n### {file_info['path']}\n```{file_info.get('language', '')}\n{file_info['content']}\n```\n"
        
        prompt = f"""You are an expert software testing engineer. Generate comprehensive unit and integration tests for the following code.

PROJECT CONTEXT:
- Languages: {', '.join(project_context['project_overview']['languages'])}
- Frameworks: {', '.join(project_context['project_overview']['frameworks'])}
- Testing Framework: Detect from project or use appropriate default (pytest for Python, Jest for JavaScript, etc.)

CODE TO TEST:
{code_content}

REQUIREMENTS:
1. Generate comprehensive unit tests covering all functions and methods
2. Include integration tests for component interactions
3. Test edge cases and error conditions
4. Use appropriate mocking where necessary
5. Follow testing best practices for the detected framework
6. Include setup and teardown methods where appropriate
7. Add meaningful test descriptions and assertions

Please provide your response in the following format:

## Test Strategy
[Brief overview of the testing approach]

## Test Files

### File: path/to/test_file.py
```python
[test code content]
```

### File: path/to/integration_test.py
```python
[integration test code content]
```

## Test Dependencies
[List any additional testing dependencies needed]

## Running the Tests
[Instructions on how to run the tests]
"""
        
        return prompt
    
    def _build_code_update_prompt(self, existing_code: str, new_requirements: str, project_context: Dict[str, Any]) -> str:
        """Build the prompt for code updates."""
        
        prompt = f"""You are an expert software developer reviewing and updating existing code. 

EXISTING CODE:
```
{existing_code}
```

NEW REQUIREMENTS:
{new_requirements}

PROJECT CONTEXT:
- Languages: {', '.join(project_context['project_overview']['languages'])}
- Frameworks: {', '.join(project_context['project_overview']['frameworks'])}

INSTRUCTIONS:
1. Review the existing code carefully
2. Implement the new requirements while maintaining existing functionality
3. Ensure backward compatibility where possible
4. Follow the existing code style and patterns
5. Add or update tests as necessary
6. Provide clear comments explaining changes

Please provide the updated code with explanations of what was changed and why.

## Changes Made
[List and explain the changes]

## Updated Code
```
[updated code content]
```

## Additional Notes
[Any important notes about the updates]
"""
        
        return prompt
    
    def _parse_code_response(self, response_content: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Claude's response to extract code files."""
        
        result = {
            'task_key': task_data.get('key', 'unknown'),
            'files': [],
            'analysis': '',
            'notes': '',
            'dependencies': []
        }
        
        lines = response_content.split('\n')
        current_section = None
        current_file = None
        current_content = []
        
        for line in lines:
            line_stripped = line.strip()
            
            # Detect sections
            if line_stripped.startswith('## Analysis'):
                current_section = 'analysis'
                continue
            elif line_stripped.startswith('## Files to Create/Modify'):
                current_section = 'files'
                continue
            elif line_stripped.startswith('## Implementation Notes'):
                current_section = 'notes'
                continue
            elif line_stripped.startswith('## Dependencies'):
                current_section = 'dependencies'
                continue
            
            # Handle file definitions
            if current_section == 'files' and line_stripped.startswith('### File:'):
                # Save previous file if exists
                if current_file:
                    result['files'].append({
                        'path': current_file,
                        'content': '\n'.join(current_content),
                        'language': self._detect_language_from_path(current_file)
                    })
                
                # Start new file
                current_file = line_stripped.replace('### File:', '').strip()
                current_content = []
                continue
            
            # Handle code blocks
            if current_section == 'files' and current_file:
                if line_stripped.startswith('```') and len(current_content) == 0:
                    continue  # Skip opening code block
                elif line_stripped.startswith('```') and len(current_content) > 0:
                    continue  # Skip closing code block
                else:
                    current_content.append(line)
            
            # Handle other sections
            elif current_section == 'analysis':
                result['analysis'] += line + '\n'
            elif current_section == 'notes':
                result['notes'] += line + '\n'
            elif current_section == 'dependencies':
                if line_stripped and not line_stripped.startswith('#'):
                    result['dependencies'].append(line_stripped)
        
        # Don't forget the last file
        if current_file and current_content:
            result['files'].append({
                'path': current_file,
                'content': '\n'.join(current_content),
                'language': self._detect_language_from_path(current_file)
            })
        
        return result
    
    def _parse_test_response(self, response_content: str) -> Dict[str, Any]:
        """Parse Claude's response to extract test files."""
        
        result = {
            'test_files': [],
            'strategy': '',
            'dependencies': [],
            'run_instructions': ''
        }
        
        lines = response_content.split('\n')
        current_section = None
        current_file = None
        current_content = []
        
        for line in lines:
            line_stripped = line.strip()
            
            # Detect sections
            if line_stripped.startswith('## Test Strategy'):
                current_section = 'strategy'
                continue
            elif line_stripped.startswith('## Test Files'):
                current_section = 'files'
                continue
            elif line_stripped.startswith('## Test Dependencies'):
                current_section = 'dependencies'
                continue
            elif line_stripped.startswith('## Running the Tests'):
                current_section = 'instructions'
                continue
            
            # Handle file definitions
            if current_section == 'files' and line_stripped.startswith('### File:'):
                # Save previous file if exists
                if current_file:
                    result['test_files'].append({
                        'path': current_file,
                        'content': '\n'.join(current_content),
                        'language': self._detect_language_from_path(current_file)
                    })
                
                # Start new file
                current_file = line_stripped.replace('### File:', '').strip()
                current_content = []
                continue
            
            # Handle code blocks
            if current_section == 'files' and current_file:
                if line_stripped.startswith('```') and len(current_content) == 0:
                    continue  # Skip opening code block
                elif line_stripped.startswith('```') and len(current_content) > 0:
                    continue  # Skip closing code block
                else:
                    current_content.append(line)
            
            # Handle other sections
            elif current_section == 'strategy':
                result['strategy'] += line + '\n'
            elif current_section == 'dependencies':
                if line_stripped and not line_stripped.startswith('#'):
                    result['dependencies'].append(line_stripped)
            elif current_section == 'instructions':
                result['run_instructions'] += line + '\n'
        
        # Don't forget the last file
        if current_file and current_content:
            result['test_files'].append({
                'path': current_file,
                'content': '\n'.join(current_content),
                'language': self._detect_language_from_path(current_file)
            })
        
        return result
    
    def _format_directory_structure(self, structure: Dict[str, Any], indent: int = 0) -> str:
        """Format directory structure for the prompt."""
        result = ""
        for key, value in structure.items():
            result += "  " * indent + f"- {key}\n"
            if isinstance(value, dict) and value:
                result += self._format_directory_structure(value, indent + 1)
        return result
    
    def _format_important_files(self, files: List[Dict[str, Any]]) -> str:
        """Format important files context for the prompt."""
        result = ""
        for file_info in files:
            result += f"### {file_info['path']}\n"
            if 'content_preview' in file_info:
                result += f"```\n{file_info['content_preview']}\n```\n\n"
            elif 'error' in file_info:
                result += f"[Error reading file: {file_info['error']}]\n\n"
        return result
    
    def _detect_language_from_path(self, file_path: str) -> str:
        """Detect programming language from file path."""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.R': 'r',
            '.sh': 'bash',
            '.sql': 'sql',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.json': 'json',
            '.xml': 'xml',
            '.md': 'markdown'
        }
        
        import os
        _, ext = os.path.splitext(file_path)
        return extension_map.get(ext.lower(), 'text')
