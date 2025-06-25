# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### ❌ "ModuleNotFoundError: No module named 'pathspec'"

**Problem**: This error occurs when the virtual environment is not activated.

**Solutions**:

1. **Use the wrapper script (easiest)**:
   ```bash
   ./task-to-code.sh jira YOUR-ISSUE-KEY
   ```

2. **Activate virtual environment manually**:
   ```bash
   source venv/bin/activate
   python main.py jira YOUR-ISSUE-KEY
   ```

3. **Use the activation helper**:
   ```bash
   source activate_env.sh
   python main.py jira YOUR-ISSUE-KEY
   ```

### ❌ Virtual Environment Issues

**Problem**: Virtual environment not working or missing.

**Solution**: Recreate the environment:
```bash
# Remove old environment
rm -rf venv

# Create new environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Validate setup
python validate.py
```

### ❌ "Configuration file not found"

**Problem**: `config.yaml` doesn't exist.

**Solution**:
```bash
python main.py setup
# or
./task-to-code.sh setup
```

### ❌ API Connection Issues

**Problem**: Can't connect to Confluence/JIRA or Anthropic.

**Solutions**:

1. **Check API credentials**:
   ```bash
   # Test Atlassian connection
   curl -u "your-email:your-api-token" https://your-domain.atlassian.net/rest/api/3/myself
   ```

2. **Verify configuration**:
   ```bash
   python -c "from src.config import Config; c = Config(); print('Config OK')"
   ```

3. **Check network connectivity**:
   ```bash
   ping your-domain.atlassian.net
   ```

### ❌ Permission Issues

**Problem**: Can't read/write files.

**Solutions**:
```bash
# Make scripts executable
chmod +x task-to-code.sh
chmod +x activate_env.sh
chmod +x install.sh
chmod +x validate.py

# Check project path permissions
ls -la /path/to/your/project
```

### ❌ Import Errors

**Problem**: Python can't find modules.

**Solutions**:

1. **Ensure you're in the right directory**:
   ```bash
   cd /home/hcruz/scripts/task-to-code
   ```

2. **Check Python path**:
   ```bash
   python -c "import sys; print(sys.path)"
   ```

3. **Validate setup**:
   ```bash
   python validate.py
   ```

## Diagnostic Commands

### Check Environment Status
```bash
# Check if virtual environment is activated
echo $VIRTUAL_ENV

# Check Python version
python --version

# Check installed packages
pip list

# Check which Python is being used
which python
```

### Validate Installation
```bash
# Full validation
python validate.py

# Quick test
python -c "from src.pipeline import TaskToCodePipeline; print('Pipeline OK')"

# Test project analysis
python examples.py analyze
```

### Debug Configuration
```bash
# Check configuration
python -c "
from src.config import Config
config = Config()
print('Confluence URL:', config.get('confluence.base_url'))
print('Project Path:', config.get('project.repository_path'))
print('Anthropic Key:', 'SET' if config.get('anthropic.api_key') else 'NOT SET')
"
```

## Environment Variables

Sometimes it helps to set these environment variables:

```bash
# Enable debug mode
export DEBUG=1

# Set Python path explicitly
export PYTHONPATH="/home/hcruz/scripts/task-to-code/src:$PYTHONPATH"

# Force UTF-8 encoding
export PYTHONIOENCODING=utf-8
```

## Clean Reinstall

If all else fails, here's how to completely reinstall:

```bash
# Remove everything
rm -rf venv/
rm -f config.yaml

# Reinstall
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Setup configuration
python main.py setup

# Validate
python validate.py
```

## Getting Help

1. **Run validation**: `python validate.py`
2. **Check documentation**: `cat README.md`
3. **Review workflow**: `cat WORKFLOW.md`
4. **Test examples**: `python examples.py analyze`

## Success Indicators

✅ `python validate.py` shows all checks passed  
✅ `./task-to-code.sh --help` shows usage information  
✅ Virtual environment is in `/home/hcruz/scripts/task-to-code/venv/`  
✅ Configuration file exists and is valid  
✅ All Python modules can be imported  

## Still Having Issues?

If you're still having problems:

1. Make sure you're in the right directory: `/home/hcruz/scripts/task-to-code`
2. Always use the wrapper script: `./task-to-code.sh`
3. Or always activate the environment first: `source venv/bin/activate`
4. Check that your configuration has real values, not placeholders
5. Ensure you have internet connectivity for API calls
