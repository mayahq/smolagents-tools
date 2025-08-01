#!/usr/bin/env python3
"""
Simple test to verify the package can be imported and basic structure works
without requiring full dependencies.
"""

def test_package_structure():
    """Test basic package structure without dependencies"""
    print("Testing smolagents-tools package structure...")
    
    try:
        # Test that we can import the package constants
        import sys
        import os
        
        # Add the package to path for testing
        package_path = os.path.join(os.path.dirname(__file__), 'smolagents_tools')
        if package_path not in sys.path:
            sys.path.insert(0, os.path.dirname(__file__))
        
        # Test importing constants that don't require smolagents
        print("✓ Testing basic imports...")
        
        # Mock the smolagents module to avoid import errors
        import types
        smolagents_mock = types.ModuleType('smolagents')
        
        class MockTool:
            def __init__(self):
                self.name = "mock_tool"
                self.description = "Mock tool for testing"
                self.inputs = {}
                self.output_type = "text"
        
        smolagents_mock.Tool = MockTool
        sys.modules['smolagents'] = smolagents_mock
        
        # Now try to import our package
        import smolagents_tools
        print(f"✓ Package version: {smolagents_tools.__version__}")
        
        # Test tool registry
        print(f"✓ Available tools: {len(smolagents_tools.AVAILABLE_TOOLS)}")
        print(f"✓ Tool categories: {list(smolagents_tools.TOOL_CATEGORIES.keys())}")
        
        # Test utility functions
        all_tools = smolagents_tools.list_tools()
        print(f"✓ Total tools listed: {len(all_tools)}")
        
        execution_tools = smolagents_tools.list_tools("execution")
        print(f"✓ Execution tools: {execution_tools}")
        
        # Test tool creation (should work with mocked smolagents)
        bash_tool_class = smolagents_tools.get_tool("bash")
        print(f"✓ Got bash tool class: {bash_tool_class}")
        
        if bash_tool_class:
            bash_tool = bash_tool_class()
            print(f"✓ Created bash tool instance: {bash_tool.name}")
        
        print("\n✅ Package structure test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Package structure test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_examples_syntax():
    """Test that example files have valid Python syntax"""
    print("\nTesting example files syntax...")
    
    import ast
    import os
    
    examples_dir = os.path.join(os.path.dirname(__file__), 'examples')
    python_files = [f for f in os.listdir(examples_dir) if f.endswith('.py')]
    
    for filename in python_files:
        filepath = os.path.join(examples_dir, filename)
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Parse the file to check syntax
            ast.parse(content)
            print(f"✓ {filename} - syntax OK")
            
        except SyntaxError as e:
            print(f"❌ {filename} - syntax error: {e}")
            return False
        except Exception as e:
            print(f"⚠️  {filename} - could not read: {e}")
    
    print("✅ All example files have valid syntax!")
    return True


def test_console_script():
    """Test that the console script entry point exists"""
    print("\nTesting console script entry point...")
    
    try:
        # Check if the main function exists in basic_usage
        import sys
        import os
        
        examples_path = os.path.join(os.path.dirname(__file__), 'examples')
        sys.path.insert(0, examples_path)
        
        # Try to import the main function
        from basic_usage import main
        print("✓ Console script entry point exists")
        print("✅ Console script test PASSED!")
        return True
        
    except ImportError as e:
        print(f"❌ Console script test FAILED: {e}")
        return False


if __name__ == "__main__":
    print("Smolagents Tools - Package Testing")
    print("=" * 50)
    
    success = True
    
    # Run tests
    success &= test_package_structure()
    success &= test_examples_syntax()
    success &= test_console_script()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("The package structure is working correctly.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please check the errors above.")
    
    exit(0 if success else 1)