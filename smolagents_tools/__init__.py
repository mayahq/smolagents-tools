"""
Smolagents Tools - OpenManus tools adapted for smolagents framework

This package provides a collection of tools adapted from OpenManus for use with the smolagents framework.
All tools follow the smolagents Tool interface and can be used in CodeAct loops.
"""

from .utils.base import AsyncSmolTool, SmolTool, SmolToolResult

# Import all @tool decorated functions from tools module
from .tools import (
    # Core @tool decorated functions (always available)
    bash_tool,
    python_executor_tool,
    safe_python_executor_tool,
    file_editor_tool,
    file_reader_tool,
    file_writer_tool,
    planning_tool,
)

# Import optional @tool decorated functions (may not be available due to missing dependencies)
try:
    from .tools import web_search_tool
except (ImportError, AttributeError):
    web_search_tool = None

try:
    from .tools import browser_tool
except (ImportError, AttributeError):
    browser_tool = None

try:
    from .tools import web_crawler_tool
except (ImportError, AttributeError):
    web_crawler_tool = None

try:
    from .tools import chat_completion_tool
except (ImportError, AttributeError):
    chat_completion_tool = None

try:
    from .tools import vnc_tool
except (ImportError, AttributeError):
    vnc_tool = None

try:
    from .tools import macos_tool
except (ImportError, AttributeError):
    macos_tool = None

# Import original tool classes for backward compatibility
from .tools import (
    # Core tool classes (always available)
    BashTool,
    PythonExecutorTool,
    SafePythonExecutorTool,
    FileEditorTool,
    SimpleFileReaderTool,
    SimpleFileWriterTool,
    PlanningTool,
    
    # Optional tool classes (may be None if dependencies not available)
    WebSearchTool,
    DuckDuckGoSearchTool,
    GoogleSearchTool,
    BingSearchTool,
    BrowserTool,
    SimpleBrowserTool,
    WebCrawlerTool,
    SimpleWebScraperTool,
    ChatCompletionTool,
    SimplePromptTool,
    VNCComputerUseTool,
    SimpleVNCComputerUseTool,
    MacOSUseTool,
    SimpleMacOSTool,
)

__version__ = "0.1.0"

# Tool registry for easy access (only include available tools)
_ALL_TOOLS = {
    # Core execution tools (always available)
    "bash_tool": BashTool,
    "python_executor_tool": PythonExecutorTool,
    "safe_python_executor_tool": SafePythonExecutorTool,
    
    # File operations (always available)
    "file_editor_tool": FileEditorTool,
    "file_reader_tool": SimpleFileReaderTool,
    "file_writer_tool": SimpleFileWriterTool,
    
    # Planning (always available)
    "planning_tool": PlanningTool,
    
    # Web tools (optional)
    "web_search_tool": WebSearchTool,
    "duckduckgo_search_tool": DuckDuckGoSearchTool,
    "google_search_tool": GoogleSearchTool,
    "bing_search_tool": BingSearchTool,
    "web_crawler_tool": WebCrawlerTool,
    "simple_web_scraper_tool": SimpleWebScraperTool,
    
    # Browser automation (optional)
    "browser_tool": BrowserTool,
    "simple_browser_tool": SimpleBrowserTool,
    
    # macOS automation (optional)
    "macos_tool": MacOSUseTool,
    "simple_macos_tool": SimpleMacOSTool,
    
    # AI and planning (optional)
    "chat_completion_tool": ChatCompletionTool,
    "simple_prompt_tool": SimplePromptTool,
    
    # VNC automation (optional)
    "vnc_computer_tool": VNCComputerUseTool,
    "simple_vnc_computer_tool": SimpleVNCComputerUseTool,
}

# Filter out None values (missing optional dependencies)
AVAILABLE_TOOLS = {name: tool_class for name, tool_class in _ALL_TOOLS.items() if tool_class is not None}

# Tool categories for organization (only include available tools)
_ALL_CATEGORIES = {
    "execution": ["bash_tool", "python_executor_tool", "safe_python_executor_tool"],
    "files": ["file_editor_tool", "file_reader_tool", "file_writer_tool"],
    "web": ["web_search_tool", "duckduckgo_search_tool", "google_search_tool", "bing_search_tool", "web_crawler_tool", "simple_web_scraper_tool"],
    "browser": ["browser_tool", "simple_browser_tool"],
    "macos": ["macos_tool", "simple_macos_tool"],
    "ai": ["chat_completion_tool", "simple_prompt_tool"],
    "planning": ["planning_tool"],
    "vnc": ["vnc_computer_tool", "simple_vnc_computer_tool"],
}

# Filter categories to only include available tools
TOOL_CATEGORIES = {}
for category, tools in _ALL_CATEGORIES.items():
    available_tools = [tool for tool in tools if tool in AVAILABLE_TOOLS]
    if available_tools:  # Only include categories that have available tools
        TOOL_CATEGORIES[category] = available_tools


def get_tool(tool_name: str):
    """
    Get a tool class by name.
    
    Args:
        tool_name (str): Name of the tool to get
        
    Returns:
        Tool class or None if not found
    """
    return AVAILABLE_TOOLS.get(tool_name)


def create_tool(tool_name: str):
    """
    Create an instance of a tool by name.
    
    Args:
        tool_name (str): Name of the tool to create
        
    Returns:
        Tool instance or None if not found
    """
    tool_class = get_tool(tool_name)
    if tool_class:
        return tool_class()
    return None


def list_tools(category: str = None):
    """
    List available tools, optionally filtered by category.
    
    Args:
        category (str): Optional category to filter by
        
    Returns:
        List of tool names
    """
    if category:
        return TOOL_CATEGORIES.get(category, [])
    return list(AVAILABLE_TOOLS.keys())


def get_tool_info(tool_name: str):
    """
    Get information about a tool.
    
    Args:
        tool_name (str): Name of the tool
        
    Returns:
        Dict with tool information
    """
    tool_class = get_tool(tool_name)
    if not tool_class:
        return None
    
    # Create temporary instance to get info
    tool = tool_class()
    
    return {
        "name": tool.name,
        "description": tool.description,
        "inputs": tool.inputs,
        "output_type": tool.output_type,
        "class": tool_class.__name__,
        "module": tool_class.__module__
    }


def create_tool_suite(tool_names: list = None):
    """
    Create a suite of tools for use in smolagents.
    
    Args:
        tool_names (list): List of tool names to include. If None, includes all tools.
        
    Returns:
        List of tool instances
    """
    if tool_names is None:
        tool_names = list(AVAILABLE_TOOLS.keys())
    
    tools = []
    for name in tool_names:
        tool = create_tool(name)
        if tool:
            tools.append(tool)
    
    return tools


# Convenience function to create common tool sets
def create_basic_toolset():
    """Create a basic set of commonly used tools"""
    return create_tool_suite([
        "bash_tool",
        "python_executor_tool",
        "file_editor_tool",
        "web_search_tool",
        "simple_browser_tool"
    ])


def create_web_toolset():
    """Create a toolset focused on web operations"""
    return create_tool_suite([
        "web_search_tool",
        "web_crawler_tool",
        "browser_tool",
        "simple_web_scraper_tool"
    ])


def create_development_toolset():
    """Create a toolset for software development"""
    return create_tool_suite([
        "bash_tool",
        "python_executor_tool",
        "file_editor_tool",
        "file_reader_tool",
        "file_writer_tool",
        "web_search_tool",
        "planning_tool"
    ])


def create_ai_toolset():
    """Create a toolset with AI capabilities"""
    return create_tool_suite([
        "chat_completion_tool",
        "simple_prompt_tool",
        "web_search_tool",
        "planning_tool",
        "file_editor_tool"
    ])


# Export all available @tool decorated functions and tool classes
_TOOL_FUNCTIONS = [
    # Core @tool decorated functions (always available)
    "bash_tool",
    "python_executor_tool",
    "safe_python_executor_tool",
    "file_editor_tool",
    "file_reader_tool",
    "file_writer_tool",
    "planning_tool",
]

_OPTIONAL_TOOL_FUNCTIONS = [
    # Optional @tool decorated functions
    "web_search_tool",
    "browser_tool",
    "web_crawler_tool",
    "chat_completion_tool",
    "vnc_tool",
    "macos_tool",
]

_TOOL_CLASSES = [
    # Core tool classes (always available)
    "BashTool",
    "PythonExecutorTool",
    "SafePythonExecutorTool",
    "FileEditorTool",
    "SimpleFileReaderTool",
    "SimpleFileWriterTool",
    "PlanningTool",
    
    # Optional tool classes
    "WebSearchTool",
    "DuckDuckGoSearchTool",
    "GoogleSearchTool",
    "BingSearchTool",
    "BrowserTool",
    "SimpleBrowserTool",
    "WebCrawlerTool",
    "SimpleWebScraperTool",
    "MacOSUseTool",
    "SimpleMacOSTool",
    "ChatCompletionTool",
    "SimplePromptTool",
    "VNCComputerUseTool",
    "SimpleVNCComputerUseTool",
]

_BASE_EXPORTS = [
    # Base classes
    "AsyncSmolTool",
    "SmolTool",
    "SmolToolResult",
    
    # Utility functions
    "get_tool",
    "create_tool",
    "list_tools",
    "get_tool_info",
    "create_tool_suite",
    "create_basic_toolset",
    "create_web_toolset",
    "create_development_toolset",
    "create_ai_toolset",
    
    # Constants
    "AVAILABLE_TOOLS",
    "TOOL_CATEGORIES",
]

# Only export tool functions and classes that are actually available
available_tool_functions = []
for func_name in _TOOL_FUNCTIONS:
    if globals().get(func_name) is not None:
        available_tool_functions.append(func_name)

available_optional_tool_functions = []
for func_name in _OPTIONAL_TOOL_FUNCTIONS:
    if globals().get(func_name) is not None:
        available_optional_tool_functions.append(func_name)

available_tool_classes = []
for class_name in _TOOL_CLASSES:
    if globals().get(class_name) is not None:
        available_tool_classes.append(class_name)

__all__ = _BASE_EXPORTS + available_tool_functions + available_optional_tool_functions + available_tool_classes