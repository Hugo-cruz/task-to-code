"""
Test suite for the task-to-code pipeline.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path

# Test data
SAMPLE_CONFIG = """
confluence:
  base_url: "https://test.atlassian.net"
  username: "test@example.com"
  api_token: "test-token"

project:
  repository_path: "/tmp/test-project"
  exclude_patterns:
    - "*.git*"
    - "__pycache__"

anthropic:
  api_key: "test-key"
  model: "claude-3-5-sonnet-20241022"
  max_tokens: 4000

output:
  generated_code_path: "./generated"
  test_path: "./tests"
  backup_existing: true
"""

SAMPLE_JIRA_RESPONSE = {
    "key": "TEST-123",
    "fields": {
        "summary": "Test Issue",
        "description": "This is a test issue description",
        "issuetype": {"name": "Story"},
        "priority": {"name": "High"},
        "status": {"name": "To Do"},
        "labels": ["backend", "api"],
        "components": [{"name": "API"}],
        "subtasks": []
    },
    "renderedFields": {
        "description": "This is a test issue description with acceptance criteria:\n- Should do X\n- Should do Y"
    }
}


class TestConfig:
    """Test configuration management."""
    
    def test_config_loading(self):
        """Test configuration loading from YAML."""
        from src.config import Config
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(SAMPLE_CONFIG)
            f.flush()
            
            config = Config(f.name)
            
            assert config.confluence_config['base_url'] == "https://test.atlassian.net"
            assert config.project_config['repository_path'] == "/tmp/test-project"
            assert config.anthropic_config['api_key'] == "test-key"
            
            os.unlink(f.name)
    
    def test_config_validation(self):
        """Test configuration validation."""
        from src.config import Config
        
        invalid_config = """
confluence:
  base_url: "your-domain.atlassian.net"
  username: "your-email@example.com"
  api_token: "your-api-token"
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(invalid_config)
            f.flush()
            
            with pytest.raises(ValueError, match="Please set a valid value"):
                Config(f.name)
            
            os.unlink(f.name)


class TestProjectAnalyzer:
    """Test project structure analysis."""
    
    def setup_method(self):
        """Setup test project structure."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create sample project structure
        (Path(self.test_dir) / "src").mkdir()
        (Path(self.test_dir) / "tests").mkdir()
        (Path(self.test_dir) / "src" / "main.py").write_text("print('hello')")
        (Path(self.test_dir) / "src" / "__init__.py").write_text("")
        (Path(self.test_dir) / "tests" / "test_main.py").write_text("def test_main(): pass")
        (Path(self.test_dir) / "README.md").write_text("# Test Project")
        (Path(self.test_dir) / "requirements.txt").write_text("requests>=2.0.0")
    
    def teardown_method(self):
        """Cleanup test files."""
        shutil.rmtree(self.test_dir)
    
    def test_project_structure_analysis(self):
        """Test project structure analysis."""
        from src.project_analyzer import ProjectAnalyzer
        
        analyzer = ProjectAnalyzer(self.test_dir)
        structure = analyzer.get_project_structure()
        
        assert structure['total_files'] >= 5
        assert structure['total_directories'] >= 2
        assert 'Python' in structure['languages']
        
        # Check specific files exist
        file_paths = [f['path'] for f in structure['files']]
        assert 'src/main.py' in file_paths
        assert 'README.md' in file_paths
    
    def test_context_summary(self):
        """Test context summary generation."""
        from src.project_analyzer import ProjectAnalyzer
        
        analyzer = ProjectAnalyzer(self.test_dir)
        context = analyzer.get_context_summary()
        
        assert 'project_overview' in context
        assert 'directory_structure' in context
        assert 'important_files' in context
        
        assert context['project_overview']['languages'] == ['Python']


class TestConfluenceClient:
    """Test Confluence/JIRA client."""
    
    def test_jira_issue_details_parsing(self):
        """Test parsing JIRA issue details."""
        from src.confluence_client import ConfluenceJiraClient
        
        # Mock the client
        client = ConfluenceJiraClient("https://test.atlassian.net", "test", "token")
        
        # Test the parsing method directly
        details = client._extract_acceptance_criteria(SAMPLE_JIRA_RESPONSE['renderedFields']['description'])
        
        assert len(details) == 2
        assert "Should do X" in details
        assert "Should do Y" in details


class TestClaudeGenerator:
    """Test Claude code generation."""
    
    def test_language_detection(self):
        """Test programming language detection from file paths."""
        from src.claude_generator import ClaudeCodeGenerator
        
        generator = ClaudeCodeGenerator("test-key")
        
        assert generator._detect_language_from_path("test.py") == "python"
        assert generator._detect_language_from_path("test.js") == "javascript"
        assert generator._detect_language_from_path("test.ts") == "typescript"
        assert generator._detect_language_from_path("test.unknown") == "text"
    
    def test_code_response_parsing(self):
        """Test parsing of Claude's code response."""
        from src.claude_generator import ClaudeCodeGenerator
        
        generator = ClaudeCodeGenerator("test-key")
        
        sample_response = """
## Analysis
This is a test analysis.

## Files to Create/Modify

### File: src/test.py
```python
def test_function():
    return "hello"
```

### File: src/utils.py
```python
def helper():
    pass
```

## Implementation Notes
Some notes here.

## Dependencies
- pytest>=7.0.0
- requests>=2.0.0
"""
        
        result = generator._parse_code_response(sample_response, {"key": "TEST-123"})
        
        assert result['task_key'] == "TEST-123"
        assert len(result['files']) == 2
        assert result['files'][0]['path'] == "src/test.py"
        assert "def test_function():" in result['files'][0]['content']
        assert len(result['dependencies']) == 2


if __name__ == "__main__":
    pytest.main([__file__])
