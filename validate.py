#!/usr/bin/env python3
"""
Validation script to test the task-to-code pipeline setup.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def check_python_version():
    """Check Python version."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (Requires 3.8+)")
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        ('requests', 'requests'),
        ('yaml', 'pyyaml'),
        ('anthropic', 'anthropic'),
        ('pathspec', 'pathspec'),
        ('jinja2', 'jinja2')
    ]
    
    missing = []
    
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            print(f"   ✅ {package_name}")
        except ImportError:
            print(f"   ❌ {package_name} (missing)")
            missing.append(package_name)
    
    if missing:
        print(f"\n💡 Install missing packages: pip install {' '.join(missing)}")
        return False
    
    return True

def check_configuration():
    """Check configuration file."""
    print("\n⚙️  Checking configuration...")
    
    config_file = Path('config.yaml')
    template_file = Path('config.template.yaml')
    
    if not template_file.exists():
        print("   ❌ config.template.yaml not found")
        return False
    else:
        print("   ✅ config.template.yaml found")
    
    if not config_file.exists():
        print("   ⚠️  config.yaml not found (run: python main.py setup)")
        return False
    
    try:
        from src.config import Config
        config = Config('config.yaml')
        print("   ✅ config.yaml valid")
        
        # Check if values are filled in
        if config.get('confluence.base_url', '').startswith('your-'):
            print("   ⚠️  Please update config.yaml with your actual values")
            return False
        
        print("   ✅ Configuration appears complete")
        return True
        
    except Exception as e:
        print(f"   ❌ config.yaml error: {e}")
        return False

def check_project_structure():
    """Check project structure."""
    print("\n📁 Checking project structure...")
    
    required_files = [
        'main.py',
        'requirements.txt',
        'src/__init__.py',
        'src/config.py',
        'src/confluence_client.py',
        'src/project_analyzer.py',
        'src/claude_generator.py',
        'src/pipeline.py'
    ]
    
    all_good = True
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (missing)")
            all_good = False
    
    return all_good

def test_imports():
    """Test if all modules can be imported."""
    print("\n🔧 Testing module imports...")
    
    modules = [
        'src.config',
        'src.confluence_client', 
        'src.project_analyzer',
        'src.claude_generator',
        'src.pipeline'
    ]
    
    all_good = True
    
    for module in modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError as e:
            print(f"   ❌ {module}: {e}")
            all_good = False
    
    return all_good

def test_basic_functionality():
    """Test basic functionality."""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test project analyzer on current directory
        from src.project_analyzer import ProjectAnalyzer
        analyzer = ProjectAnalyzer('.')
        structure = analyzer.get_project_structure()
        print(f"   ✅ Project analyzer (found {structure['total_files']} files)")
        
        # Test Claude generator (without API call)
        from src.claude_generator import ClaudeCodeGenerator
        generator = ClaudeCodeGenerator('test-key')
        lang = generator._detect_language_from_path('test.py')
        print(f"   ✅ Claude generator (detected language: {lang})")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Basic functionality test failed: {e}")
        return False

def main():
    """Run all validation checks."""
    print("🔍 Task-to-Code Pipeline Validation\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Configuration", check_configuration),
        ("Project Structure", check_project_structure),
        ("Module Imports", test_imports),
        ("Basic Functionality", test_basic_functionality)
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ {name} check failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 VALIDATION SUMMARY")
    print("="*50)
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:8} {name}")
        if result:
            passed += 1
    
    print(f"\nResult: {passed}/{len(results)} checks passed")
    
    if passed == len(results):
        print("\n🎉 All checks passed! The pipeline is ready to use.")
        print("\nNext steps:")
        print("1. Update config.yaml with your API credentials")
        print("2. Set your project repository path")
        print("3. Run: python main.py jira YOUR-ISSUE-KEY")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nFor help:")
        print("- Check the README.md file")
        print("- Run: python main.py --help")
        print("- Review the WORKFLOW.md documentation")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
