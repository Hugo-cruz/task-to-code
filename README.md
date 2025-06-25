# Task-to-Code Pipeline

A Python pipeline that extracts data from Confluence/JIRA tasks, analyzes project structure, and generates code with tests using Claude AI.

## Features

- 📋 Extract task data from Confluence pages and JIRA issues
- 🔍 Analyze project structure and gather context
- 🤖 Generate code using Claude AI (Anthropic)
- ✅ Create comprehensive unit and integration tests
- 🔄 Update existing code based on new requirements
- 💾 Backup existing files before modifications
- 📊 Generate detailed reports of the process

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configuration

Copy the template configuration file and fill in your values:

```bash
python main.py setup
```

This will create a `config.yaml` file. You need to fill in:

- **Confluence/JIRA API credentials**
  - Get an API token from: https://id.atlassian.com/manage-profile/security/api-tokens
- **Project repository path** (local path to your project)
- **Anthropic API key** (for Claude AI)

### 3. Project Structure

```
task-to-code/
├── config.template.yaml    # Configuration template
├── config.yaml            # Your configuration (created by setup)
├── main.py                # CLI interface
├── requirements.txt       # Python dependencies
├── src/                   # Source code
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── confluence_client.py # Confluence/JIRA API client
│   ├── project_analyzer.py  # Project structure analyzer
│   ├── claude_generator.py  # Claude AI code generator
│   └── pipeline.py        # Main pipeline orchestrator
├── generated/             # Generated code output (created automatically)
└── tests/                 # Generated tests (created automatically)
```

## Usage

### Method 1: Wrapper Script (Recommended)

The easiest way to use the pipeline is with the wrapper script that automatically handles the virtual environment:

```bash
# Process a JIRA issue
./task-to-code.sh jira PROJ-123

# Process a Confluence page
./task-to-code.sh confluence 123456789

# Update existing code
./task-to-code.sh update "src/myfile.py" "Add error handling"
```

### Method 2: Manual Virtual Environment Activation

```bash
# Activate virtual environment
source venv/bin/activate

# Or use the activation helper
source activate_env.sh

# Then run commands
python main.py jira PROJ-123
```

### Process a JIRA Issue

```bash
./task-to-code.sh jira PROJ-123
```

This will:
1. Extract task details from JIRA
2. Analyze your project structure
3. Generate code based on the task requirements
4. Create unit and integration tests
5. Save everything to the `generated/` directory

### Process a Confluence Page

```bash
python main.py confluence 123456789
```

Similar to JIRA processing, but extracts requirements from a Confluence page.

### Update Existing Code

```bash
python main.py update "src/myfile.py" "Add error handling and logging"
```

This will:
1. Read the existing file
2. Generate updated code based on your requirements
3. Create a backup of the original file
4. Update the file with the new code

### Run Tests

```bash
python main.py test
```

Get instructions on how to run the tests for your project.

## Configuration

The `config.yaml` file contains all the necessary configuration:

```yaml
# Confluence/JIRA API Configuration
confluence:
  base_url: "https://your-domain.atlassian.net"
  username: "your-email@example.com"
  api_token: "your-api-token"

# Project Configuration  
project:
  repository_path: "/path/to/your/project"
  exclude_patterns:
    - "*.git*"
    - "node_modules"
    - "__pycache__"
    # ... more patterns

# Anthropic Claude API Configuration
anthropic:
  api_key: "your-anthropic-api-key"
  model: "claude-3-5-sonnet-20241022"
  max_tokens: 4000

# Output Configuration
output:
  generated_code_path: "./generated"
  test_path: "./tests"
  backup_existing: true
```

## API Keys

### Atlassian API Token
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Create a new API token
3. Use your email as username and the token as password

### Anthropic API Key
1. Sign up at https://www.anthropic.com/
2. Go to your API settings
3. Create a new API key

## Generated Output

For each processed task, the pipeline creates:

```
generated/
└── PROJ-123/              # Issue-specific directory
    ├── code/              # Generated code files
    │   ├── feature.py
    │   └── utils.py
    ├── tests/             # Generated test files
    │   ├── test_feature.py
    │   └── test_utils.py
    ├── summary.json       # Detailed processing report
    └── summary.md         # Human-readable report
```

## Pipeline Steps

1. **Extract Task Data**: Get requirements from Confluence/JIRA
2. **Analyze Project**: Scan project structure and gather context
3. **Generate Code**: Use Claude AI to create implementation
4. **Generate Tests**: Create comprehensive test suites
5. **Save Files**: Organize output in structured directories
6. **Create Reports**: Generate detailed processing reports

## Examples

### Example JIRA Task Processing

```bash
$ python main.py jira BACKEND-456

Processing JIRA task: BACKEND-456
1. Extracting task data from JIRA...
2. Analyzing project structure...
3. Generating code with Claude AI...
4. Generating tests...
5. Saving generated files...

✅ Task processing completed! Check the output directory: ./generated

✅ Successfully processed JIRA issue: BACKEND-456
Generated 4 files

📦 Dependencies to install:
  - pytest-mock>=3.11.0
  - requests-mock>=1.9.0
```

### Example Code Update

```bash
$ python main.py update "src/api.py" "Add rate limiting and retry logic"

Updating existing code: src/api.py
Backup created: /path/to/project/src/api.backup_20240625_143022.py

✅ Code updated successfully!
```

## Error Handling

The pipeline includes comprehensive error handling:

- Configuration validation
- API connection testing  
- File system permissions
- Invalid task IDs
- Network connectivity issues

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
1. Check the configuration is correct
2. Verify API credentials
3. Ensure project path exists and is accessible
4. Check the generated reports for detailed error information
