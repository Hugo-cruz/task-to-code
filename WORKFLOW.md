# Task-to-Code Pipeline Workflow

This document describes the complete workflow for using the task-to-code pipeline.

## Quick Start

### 1. Installation

```bash
# Clone or download the project
cd task-to-code

# Run the installation script
./install.sh

# Or install manually:
pip install -r requirements.txt
python main.py setup
```

### 2. Configuration

Edit `config.yaml` with your credentials:

```yaml
confluence:
  base_url: "https://your-company.atlassian.net"
  username: "your-email@company.com"
  api_token: "your-atlassian-api-token"

project:
  repository_path: "/path/to/your/project"

anthropic:
  api_key: "your-anthropic-api-key"
```

### 3. First Run

```bash
# Process a JIRA issue
python main.py jira PROJ-123

# Or process a Confluence page
python main.py confluence 123456789
```

## Detailed Workflow

### Step 1: Task Analysis

The pipeline first extracts comprehensive information from your task:

**For JIRA Issues:**
- Title and description
- Acceptance criteria
- Issue type and priority
- Labels and components
- Subtasks

**For Confluence Pages:**
- Page title and content
- Requirements extraction
- Context analysis

### Step 2: Project Context

The pipeline analyzes your project to understand:

- **Languages and frameworks** used
- **Directory structure** and organization
- **Important files** (configs, main files, etc.)
- **Existing patterns** and conventions
- **Dependencies** and build tools

### Step 3: Code Generation

Using Claude AI, the pipeline generates:

- **Implementation code** following your project patterns
- **Configuration files** if needed
- **Database migrations** (if applicable)
- **API endpoints** (if applicable)
- **Utility functions** and helpers

### Step 4: Test Generation

Comprehensive test suites are created:

- **Unit tests** for individual functions
- **Integration tests** for component interactions
- **Mock data** and fixtures
- **Edge case testing**
- **Error condition handling**

### Step 5: Output Organization

Generated files are organized in a structured way:

```
generated/
└── PROJ-123/
    ├── code/
    │   ├── feature.py
    │   ├── models.py
    │   └── utils.py
    ├── tests/
    │   ├── test_feature.py
    │   ├── test_models.py
    │   └── test_utils.py
    ├── summary.json
    └── summary.md
```

## Best Practices

### Writing Good Task Descriptions

For best results, ensure your tasks include:

1. **Clear requirements**: What needs to be built?
2. **Acceptance criteria**: How will you know it's done?
3. **Context**: How does this fit into the larger system?
4. **Constraints**: Any limitations or requirements?

**Example Good Task:**
```
Title: Add user authentication API endpoint

Description:
Create a REST API endpoint for user authentication that accepts email/password
and returns a JWT token.

Acceptance Criteria:
- POST /api/auth/login endpoint
- Accepts JSON with email and password
- Returns JWT token on success
- Returns 401 on invalid credentials
- Rate limiting: max 5 attempts per minute
- Logs authentication attempts
- Unit tests with >90% coverage
```

### Project Organization

Ensure your project has:

- Clear directory structure
- Consistent naming conventions
- Configuration files (requirements.txt, package.json, etc.)
- Existing code examples
- Documentation

### Review Process

After generation:

1. **Review generated code** for quality and correctness
2. **Run tests** to ensure they pass
3. **Check integration** with existing code
4. **Update documentation** if necessary
5. **Commit changes** with descriptive messages

## Advanced Usage

### Custom Prompts

You can modify the prompt generation in `src/claude_generator.py` to:

- Add specific coding standards
- Include additional context
- Customize test generation
- Add framework-specific instructions

### Integration with CI/CD

Add pipeline integration:

```yaml
# .github/workflows/task-to-code.yml
name: Task to Code
on:
  issue_comment:
    types: [created]

jobs:
  generate:
    if: contains(github.event.comment.body, '/generate-code')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Generate code
        run: python main.py jira ${{ github.event.issue.number }}
```

### Custom Analyzers

Extend `ProjectAnalyzer` to add:

- Framework-specific analysis
- Security pattern detection
- Performance optimization suggestions
- Architecture compliance checking

## Troubleshooting

### Common Issues

**Configuration Errors:**
```bash
# Verify config
python -c "from src.config import Config; Config()"
```

**API Connection Issues:**
```bash
# Test Atlassian connection
curl -u email@company.com:api-token https://company.atlassian.net/rest/api/3/myself
```

**Project Path Issues:**
```bash
# Verify project path
python -c "from src.project_analyzer import ProjectAnalyzer; ProjectAnalyzer('/path/to/project').get_project_structure()"
```

### Debug Mode

Enable detailed logging by setting environment variable:
```bash
export DEBUG=1
python main.py jira PROJ-123
```

### Getting Help

1. Check the generated `summary.md` file for detailed information
2. Review the `summary.json` for technical details
3. Look at example outputs in the `generated/` directory
4. Check project documentation and README

## Examples

See `examples.py` for complete working examples:

```bash
# Analyze current project
python examples.py analyze

# Test JIRA processing (with sample data)
python examples.py jira

# Test code updates
python examples.py update
```

## Next Steps

1. **Integrate with your workflow**: Add to your development process
2. **Customize for your team**: Modify prompts and templates
3. **Automate further**: Connect to CI/CD pipelines
4. **Scale up**: Process multiple tasks in batch
5. **Monitor and improve**: Track generated code quality
