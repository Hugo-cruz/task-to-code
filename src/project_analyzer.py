"""Project structure analyzer for gathering context about the codebase."""

import os
import pathspec
from pathlib import Path
from typing import Dict, List, Any, Optional
import fnmatch


class ProjectAnalyzer:
    """Analyzes project structure and extracts relevant context."""
    
    def __init__(self, repository_path: str, exclude_patterns: Optional[List[str]] = None):
        """
        Initialize the project analyzer.
        
        Args:
            repository_path: Path to the project repository
            exclude_patterns: List of patterns to exclude from analysis
        """
        self.repository_path = Path(repository_path)
        self.exclude_patterns = exclude_patterns or [
            "*.git*", "node_modules", "*.pyc", "__pycache__", 
            "*.log", "dist", "build", ".env", "*.egg-info",
            ".pytest_cache", ".mypy_cache", "coverage.xml"
        ]
        
        # Create pathspec for pattern matching
        self.spec = pathspec.PathSpec.from_lines('gitwildmatch', self.exclude_patterns)
    
    def get_project_structure(self) -> Dict[str, Any]:
        """
        Get the complete project structure.
        
        Returns:
            Dictionary containing project structure information
        """
        if not self.repository_path.exists():
            raise FileNotFoundError(f"Repository path does not exist: {self.repository_path}")
        
        structure = {
            'root_path': str(self.repository_path),
            'directories': [],
            'files': [],
            'file_tree': self._build_file_tree(),
            'languages': self._detect_languages(),
            'frameworks': self._detect_frameworks(),
            'total_files': 0,
            'total_directories': 0
        }
        
        # Walk through the directory structure
        for root, dirs, files in os.walk(self.repository_path):
            root_path = Path(root)
            relative_root = root_path.relative_to(self.repository_path)
            
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not self._should_exclude(relative_root / d)]
            
            # Add directory info
            if not self._should_exclude(relative_root):
                structure['directories'].append({
                    'path': str(relative_root),
                    'absolute_path': str(root_path),
                    'file_count': len([f for f in files if not self._should_exclude(relative_root / f)])
                })
                structure['total_directories'] += 1
            
            # Add file info
            for file in files:
                file_path = relative_root / file
                if not self._should_exclude(file_path):
                    structure['files'].append({
                        'path': str(file_path),
                        'absolute_path': str(root_path / file),
                        'extension': Path(file).suffix,
                        'size': (root_path / file).stat().st_size,
                        'name': file
                    })
                    structure['total_files'] += 1
        
        return structure
    
    def get_relevant_files(self, keywords: List[str], file_extensions: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get files that are relevant to the given keywords.
        
        Args:
            keywords: List of keywords to search for
            file_extensions: List of file extensions to filter by
            
        Returns:
            List of relevant file information
        """
        relevant_files = []
        structure = self.get_project_structure()
        
        for file_info in structure['files']:
            file_path = Path(file_info['absolute_path'])
            
            # Filter by extension if specified
            if file_extensions and file_info['extension'] not in file_extensions:
                continue
            
            # Check if file is relevant based on keywords
            is_relevant = False
            
            # Check filename
            for keyword in keywords:
                if keyword.lower() in file_info['name'].lower():
                    is_relevant = True
                    break
            
            # Check file content for keywords (for text files only)
            if not is_relevant:
                try:
                    if file_path.suffix in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.md', '.txt', '.yml', '.yaml', '.json']:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read().lower()
                            for keyword in keywords:
                                if keyword.lower() in content:
                                    is_relevant = True
                                    break
                except (IOError, UnicodeDecodeError):
                    continue
            
            if is_relevant:
                relevant_files.append(file_info)
        
        return relevant_files
    
    def get_file_content(self, file_path: str) -> str:
        """
        Get the content of a specific file.
        
        Args:
            file_path: Path to the file (relative to repository root)
            
        Returns:
            File content as string
        """
        full_path = self.repository_path / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding for binary files
            with open(full_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    def get_context_summary(self, max_files: int = 20) -> Dict[str, Any]:
        """
        Get a summary of the project context for code generation.
        
        Args:
            max_files: Maximum number of files to include in detailed analysis
            
        Returns:
            Dictionary with project context summary
        """
        structure = self.get_project_structure()
        
        # Get the most important files (configuration, main files, etc.)
        important_files = self._get_important_files(structure['files'], max_files)
        
        context = {
            'project_overview': {
                'total_files': structure['total_files'],
                'total_directories': structure['total_directories'],
                'languages': structure['languages'],
                'frameworks': structure['frameworks']
            },
            'directory_structure': self._get_simplified_tree(structure['file_tree']),
            'important_files': []
        }
        
        # Add content of important files
        for file_info in important_files:
            try:
                content = self.get_file_content(file_info['path'])
                context['important_files'].append({
                    'path': file_info['path'],
                    'size': file_info['size'],
                    'extension': file_info['extension'],
                    'content_preview': content[:1000] + '...' if len(content) > 1000 else content
                })
            except Exception as e:
                context['important_files'].append({
                    'path': file_info['path'],
                    'error': str(e)
                })
        
        return context
    
    def _should_exclude(self, path: Path) -> bool:
        """Check if a path should be excluded based on patterns."""
        return self.spec.match_file(str(path))
    
    def _build_file_tree(self) -> Dict[str, Any]:
        """Build a nested dictionary representing the file tree."""
        tree = {}
        
        for root, dirs, files in os.walk(self.repository_path):
            root_path = Path(root)
            relative_root = root_path.relative_to(self.repository_path)
            
            # Filter excluded items
            dirs[:] = [d for d in dirs if not self._should_exclude(relative_root / d)]
            files = [f for f in files if not self._should_exclude(relative_root / f)]
            
            if self._should_exclude(relative_root):
                continue
            
            # Build nested structure
            current = tree
            if str(relative_root) != '.':
                for part in relative_root.parts:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
            
            # Add files and directories
            for d in dirs:
                if d not in current:
                    current[d] = {}
            
            for f in files:
                current[f] = None  # Files are leaf nodes
        
        return tree
    
    def _detect_languages(self) -> List[str]:
        """Detect programming languages used in the project."""
        languages = set()
        
        language_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.R': 'R',
            '.m': 'Objective-C',
            '.sh': 'Shell',
            '.sql': 'SQL'
        }
        
        for root, dirs, files in os.walk(self.repository_path):
            root_path = Path(root)
            relative_root = root_path.relative_to(self.repository_path)
            
            if self._should_exclude(relative_root):
                continue
            
            for file in files:
                file_path = relative_root / file
                if not self._should_exclude(file_path):
                    ext = Path(file).suffix.lower()
                    if ext in language_extensions:
                        languages.add(language_extensions[ext])
        
        return sorted(list(languages))
    
    def _detect_frameworks(self) -> List[str]:
        """Detect frameworks and libraries used in the project."""
        frameworks = set()
        
        # Check for common framework indicators
        framework_indicators = {
            'package.json': ['React', 'Angular', 'Vue', 'Express', 'Next.js'],
            'requirements.txt': ['Django', 'Flask', 'FastAPI', 'Pandas', 'NumPy'],
            'pom.xml': ['Spring', 'Maven'],
            'build.gradle': ['Spring', 'Gradle'],
            'Gemfile': ['Rails', 'Sinatra'],
            'composer.json': ['Laravel', 'Symfony'],
            'Cargo.toml': ['Rust'],
            'go.mod': ['Go']
        }
        
        for indicator_file, possible_frameworks in framework_indicators.items():
            try:
                content = self.get_file_content(indicator_file).lower()
                for framework in possible_frameworks:
                    if framework.lower() in content:
                        frameworks.add(framework)
            except FileNotFoundError:
                continue
        
        return sorted(list(frameworks))
    
    def _get_important_files(self, files: List[Dict[str, Any]], max_files: int) -> List[Dict[str, Any]]:
        """Get the most important files for understanding the project."""
        important_patterns = [
            'readme*', 'license*', 'package.json', 'requirements.txt',
            'setup.py', 'pyproject.toml', 'pom.xml', 'build.gradle',
            'dockerfile', 'docker-compose*', 'makefile', '.gitignore',
            'main.*', 'app.*', 'index.*', '__init__.py', 'config.*'
        ]
        
        important_files = []
        regular_files = []
        
        for file_info in files:
            file_name = file_info['name'].lower()
            is_important = any(fnmatch.fnmatch(file_name, pattern) for pattern in important_patterns)
            
            if is_important:
                important_files.append(file_info)
            else:
                regular_files.append(file_info)
        
        # Sort by importance and size
        important_files.sort(key=lambda x: (x['name'].lower(), x['size']))
        regular_files.sort(key=lambda x: x['size'], reverse=True)
        
        # Combine and limit
        result = important_files + regular_files
        return result[:max_files]
    
    def _get_simplified_tree(self, tree: Dict[str, Any], max_depth: int = 3, current_depth: int = 0) -> Dict[str, Any]:
        """Get a simplified version of the file tree for context."""
        if current_depth >= max_depth:
            return {"...": "truncated"}
        
        simplified = {}
        for key, value in tree.items():
            if isinstance(value, dict):
                if value:  # Non-empty directory
                    simplified[key + '/'] = self._get_simplified_tree(value, max_depth, current_depth + 1)
                else:
                    simplified[key + '/'] = {}
            else:
                simplified[key] = None
        
        return simplified
