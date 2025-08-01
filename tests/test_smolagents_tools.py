import pytest
from smolagents_tools import (
    get_tool, 
    create_tool, 
    list_tools, 
    get_tool_info,
    create_basic_toolset,
    create_web_toolset,
    create_development_toolset,
    create_ai_toolset,
    AVAILABLE_TOOLS,
    TOOL_CATEGORIES
)


def test_tool_registry():
    """Test that the tool registry is properly populated"""
    assert len(AVAILABLE_TOOLS) > 0
    assert len(TOOL_CATEGORIES) > 0
    
    # Check that some expected tools are available
    expected_tools = ["bash", "python_executor", "file_editor", "web_search"]
    for tool_name in expected_tools:
        assert tool_name in AVAILABLE_TOOLS


def test_get_tool():
    """Test getting tool classes by name"""
    bash_tool_class = get_tool("bash")
    assert bash_tool_class is not None
    
    # Test non-existent tool
    non_existent = get_tool("non_existent_tool")
    assert non_existent is None


def test_create_tool():
    """Test creating tool instances"""
    bash_tool = create_tool("bash")
    assert bash_tool is not None
    assert hasattr(bash_tool, 'forward')
    
    # Test non-existent tool
    non_existent = create_tool("non_existent_tool")
    assert non_existent is None


def test_list_tools():
    """Test listing tools"""
    all_tools = list_tools()
    assert len(all_tools) > 0
    
    # Test category filtering
    execution_tools = list_tools("execution")
    assert "bash" in execution_tools
    assert "python_executor" in execution_tools


def test_get_tool_info():
    """Test getting tool information"""
    bash_info = get_tool_info("bash")
    assert bash_info is not None
    assert "name" in bash_info
    assert "description" in bash_info
    assert "inputs" in bash_info
    
    # Test non-existent tool
    non_existent_info = get_tool_info("non_existent_tool")
    assert non_existent_info is None


def test_create_basic_toolset():
    """Test creating basic toolset"""
    tools = create_basic_toolset()
    assert len(tools) > 0
    
    # Check that all tools have the required interface
    for tool in tools:
        assert hasattr(tool, 'forward')
        assert hasattr(tool, 'name')
        assert hasattr(tool, 'description')


def test_create_web_toolset():
    """Test creating web toolset"""
    tools = create_web_toolset()
    assert len(tools) > 0
    
    # Check that all tools have the required interface
    for tool in tools:
        assert hasattr(tool, 'forward')


def test_create_development_toolset():
    """Test creating development toolset"""
    tools = create_development_toolset()
    assert len(tools) > 0
    
    # Check that all tools have the required interface
    for tool in tools:
        assert hasattr(tool, 'forward')


def test_create_ai_toolset():
    """Test creating AI toolset"""
    tools = create_ai_toolset()
    assert len(tools) > 0
    
    # Check that all tools have the required interface
    for tool in tools:
        assert hasattr(tool, 'forward')


def test_tool_categories():
    """Test tool categories structure"""
    assert "execution" in TOOL_CATEGORIES
    assert "files" in TOOL_CATEGORIES
    assert "web" in TOOL_CATEGORIES
    
    # Check that category tools exist in main registry
    for category, tools in TOOL_CATEGORIES.items():
        for tool_name in tools:
            assert tool_name in AVAILABLE_TOOLS


def test_bash_tool_basic():
    """Test basic bash tool functionality"""
    bash_tool = create_tool("bash")
    assert bash_tool is not None
    
    # Test simple command
    result = bash_tool.forward(command="echo 'test'")
    assert result is not None


def test_python_executor_basic():
    """Test basic python executor functionality"""
    python_tool = create_tool("python_executor")
    assert python_tool is not None
    
    # Test simple Python code
    result = python_tool.forward(code="print('Hello, World!')")
    assert result is not None


def test_file_editor_basic():
    """Test basic file editor functionality"""
    file_tool = create_tool("file_editor")
    assert file_tool is not None
    
    # Test viewing a file (should handle non-existent files gracefully)
    result = file_tool.forward(command="view", path="/tmp/test_file_that_does_not_exist.txt")
    assert result is not None


if __name__ == "__main__":
    pytest.main([__file__])
