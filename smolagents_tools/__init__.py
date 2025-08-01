"""
Smolagents Tools - OpenManus tools adapted for smolagents framework

This package provides a collection of tools adapted from OpenManus for use with the smolagents framework.
All tools follow the smolagents Tool interface and can be used in CodeAct loops.
"""

from .base import AsyncSmolTool, SmolTool, SmolToolResult

# Core tools (always available)
from .bash import BashTool
from .python_executor import PythonExecutorTool, SafePythonExecutorTool
from .file_editor import FileEditorTool, SimpleFileReaderTool, SimpleFileWriterTool
from .planning import PlanningTool

# Optional tools (import with error handling)
try:
    from .web_search import WebSearchTool, DuckDuckGoSearchTool, GoogleSearchTool, BingSearchTool
except ImportError:
    WebSearchTool = DuckDuckGoSearchTool = GoogleSearchTool = BingSearchTool = None

try:
    from .browser import BrowserTool, SimpleBrowserTool
except ImportError:
    BrowserTool = SimpleBrowserTool = None

try:
    from .web_crawler import WebCrawlerTool, SimpleWebScraperTool
except ImportError:
    WebCrawlerTool = SimpleWebScraperTool = None

try:
    from .chat_completion import ChatCompletionTool, SimplePromptTool
except ImportError:
    ChatCompletionTool = SimplePromptTool = None

try:
    from .macos import MacOSUseTool, SimpleMacOSTool
except ImportError:
    MacOSUseTool = SimpleMacOSTool = None

__version__ = "0.1.0"

# Tool registry for easy access (only include available tools)
_ALL_TOOLS = {
    # Core execution tools (always available)
    "bash": BashTool,
    "python_executor": PythonExecutorTool,
    "safe_python_executor": SafePythonExecutorTool,
    
    # File operations (always available)
    "file_editor": FileEditorTool,
    "file_reader": SimpleFileReaderTool,
    "file_writer": SimpleFileWriterTool,
    
    # Planning (always available)
    "planning": PlanningTool,
    
    # Web tools (optional)
    "web_search": WebSearchTool,
    "duckduckgo_search": DuckDuckGoSearchTool,
    "google_search": GoogleSearchTool,
    "bing_search": BingSearchTool,
    "web_crawler": WebCrawlerTool,
    "simple_web_scraper": SimpleWebScraperTool,
    
    # Browser automation (optional)
    "browser": BrowserTool,
    "simple_browser": SimpleBrowserTool,
    
    # macOS automation (optional)
    "macos": MacOSUseTool,
    "simple_macos": SimpleMacOSTool,
    
    # AI and planning (optional)
    "chat_completion": ChatCompletionTool,
    "simple_prompt": SimplePromptTool,
}

# Filter out None values (missing optional dependencies)
AVAILABLE_TOOLS = {name: tool_class for name, tool_class in _ALL_TOOLS.items() if tool_class is not None}

# Tool categories for organization (only include available tools)
_ALL_CATEGORIES = {
    "execution": ["bash", "python_executor", "safe_python_executor"],
    "files": ["file_editor", "file_reader", "file_writer"],
    "web": ["web_search", "duckduckgo_search", "google_search", "bing_search", "web_crawler", "simple_web_scraper"],
    "browser": ["browser", "simple_browser"],
    "macos": ["macos", "simple_macos"],
    "ai": ["chat_completion", "simple_prompt"],
    "planning": ["planning"],
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
        "bash",
        "python_executor", 
        "file_editor",
        "web_search",
        "simple_browser"
    ])


def create_web_toolset():
    """Create a toolset focused on web operations"""
    return create_tool_suite([
        "web_search",
        "web_crawler",
        "browser",
        "simple_web_scraper"
    ])


def create_development_toolset():
    """Create a toolset for software development"""
    return create_tool_suite([
        "bash",
        "python_executor",
        "file_editor",
        "file_reader", 
        "file_writer",
        "web_search",
        "planning"
    ])


def create_ai_toolset():
    """Create a toolset with AI capabilities"""
    return create_tool_suite([
        "chat_completion",
        "simple_prompt",
        "web_search",
        "planning",
        "file_editor"
    ])


# Export main classes and functions (only available ones)
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

_TOOL_EXPORTS = [
    # Core tools (always available)
    "BashTool",
    "PythonExecutorTool",
    "SafePythonExecutorTool",
    "FileEditorTool",
    "SimpleFileReaderTool",
    "SimpleFileWriterTool",
    "PlanningTool",
    
    # Optional tools
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
]

# Only export tools that are actually available
available_tool_exports = []
for tool_name in _TOOL_EXPORTS:
    if globals().get(tool_name) is not None:
        available_tool_exports.append(tool_name)

__all__ = _BASE_EXPORTS + available_tool_exports