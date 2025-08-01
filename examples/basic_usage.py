"""
Basic usage examples for smolagents-tools
"""

import asyncio
from smolagents_tools import (
    BashTool, WebSearchTool, FileEditorTool, PythonExecutorTool,
    PlanningTool, create_basic_toolset
)


async def test_individual_tools():
    """Test individual tools"""
    print("=== Testing Individual Tools ===\n")
    
    # Test Bash Tool
    print("1. Testing BashTool...")
    bash = BashTool()
    result = await bash.execute(command="echo 'Hello from bash!'")
    print(f"Bash result: {result.output}")
    print()
    
    # Test Web Search Tool
    print("2. Testing WebSearchTool...")
    search = WebSearchTool()
    result = await search.execute(query="Python programming", max_results=3)
    print(f"Search result: {result.output[:200]}...")
    print()
    
    # Test File Editor Tool
    print("3. Testing FileEditorTool...")
    editor = FileEditorTool()
    
    # Create a test file
    test_content = "Hello, World!\nThis is a test file.\nLine 3"
    result = await editor.execute(
        command="create",
        path="/tmp/test_file.txt",
        file_text=test_content
    )
    print(f"File creation: {result.output}")
    
    # View the file
    result = await editor.execute(command="view", path="/tmp/test_file.txt")
    print(f"File content:\n{result.output}")
    print()
    
    # Test Python Executor Tool
    print("4. Testing PythonExecutorTool...")
    executor = PythonExecutorTool()
    code = """
import math
result = math.sqrt(16)
print(f"Square root of 16 is: {result}")
for i in range(3):
    print(f"Count: {i}")
"""
    result = await executor.execute(code=code)
    print(f"Python execution result:\n{result.output}")
    print()
    
    # Test Planning Tool
    print("5. Testing PlanningTool...")
    planner = PlanningTool()
    
    # Create a plan
    result = await planner.execute(
        action="create_plan",
        task_description="Build a simple web application"
    )
    print(f"Plan creation:\n{result.output}")
    print()


def test_smolagents_integration():
    """Test integration with smolagents (requires smolagents to be installed)"""
    print("=== Testing Smolagents Integration ===\n")
    
    try:
        from smolagents import CodeAgent, InferenceClientModel
        from smolagents_tools import create_basic_toolset
        
        print("Smolagents integration test would go here...")
        print("Note: This requires a valid model and API key")
        
        # Example of how it would work:
        # model = InferenceClientModel(model_id="Qwen/Qwen2.5-Coder-32B-Instruct")
        # tools = create_basic_toolset()
        # agent = CodeAgent(tools=tools, model=model)
        # result = agent.run("Create a simple Python script that prints hello world")
        
    except ImportError:
        print("Smolagents not installed. Install with: pip install smolagents")


def test_tool_collections():
    """Test tool collection functions"""
    print("=== Testing Tool Collections ===\n")
    
    from smolagents_tools import (
        create_basic_toolset, create_web_toolset, create_development_toolset,
        list_tools, get_tool, create_tool
    )
    
    basic_tools = create_basic_toolset()
    print(f"Basic tools count: {len(basic_tools)}")
    print(f"Basic tools: {[tool.name for tool in basic_tools]}")
    print()
    
    web_tools = create_web_toolset()
    print(f"Web tools count: {len(web_tools)}")
    print(f"Web tools: {[tool.name for tool in web_tools]}")
    print()
    
    dev_tools = create_development_toolset()
    print(f"Development tools count: {len(dev_tools)}")
    print(f"Development tools: {[tool.name for tool in dev_tools]}")
    print()
    
    all_tool_names = list_tools()
    print(f"All available tools: {len(all_tool_names)}")
    print(f"Tool names: {all_tool_names}")
    print()
    
    # Test individual tool creation
    bash_tool = create_tool("bash")
    print(f"Created bash tool: {bash_tool.name}")
    print()


def test_forward_methods():
    """Test the forward methods (smolagents interface)"""
    print("=== Testing Forward Methods (Smolagents Interface) ===\n")
    
    # Test bash tool forward method
    bash = BashTool()
    result = bash.forward(command="echo 'Hello from forward method!'")
    print(f"Bash forward result: {result}")
    print()
    
    # Test python executor forward method
    python_tool = PythonExecutorTool()
    result = python_tool.forward(code="print('Hello from Python forward!')")
    print(f"Python forward result: {result}")
    print()


async def main():
    """Main test function"""
    print("Smolagents Tools - Basic Usage Examples")
    print("=" * 50)
    print()
    
    # Test individual tools
    await test_individual_tools()
    
    # Test tool collections
    test_tool_collections()
    
    # Test forward methods
    test_forward_methods()
    
    # Test smolagents integration
    test_smolagents_integration()
    
    print("All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())