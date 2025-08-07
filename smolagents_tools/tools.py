"""
Centralized tools module with @tool decorators for smolagents
"""

try:
    from smolagents import tool
except ImportError:
    def tool(func):
        return func

# Import all tool classes from utils
from .utils.bash import BashTool as _BashTool
from .utils.python_executor import PythonExecutorTool as _PythonExecutorTool, SafePythonExecutorTool as _SafePythonExecutorTool
from .utils.file_editor import FileEditorTool as _FileEditorTool, SimpleFileReaderTool as _SimpleFileReaderTool, SimpleFileWriterTool as _SimpleFileWriterTool
from .utils.planning import PlanningTool as _PlanningTool

# Optional tools (import with error handling)
try:
    from .utils.web_search import WebSearchTool as _WebSearchTool, DuckDuckGoSearchTool as _DuckDuckGoSearchTool, GoogleSearchTool as _GoogleSearchTool, BingSearchTool as _BingSearchTool
except ImportError:
    _WebSearchTool = _DuckDuckGoSearchTool = _GoogleSearchTool = _BingSearchTool = None

try:
    from .utils.browser import BrowserTool as _BrowserTool, SimpleBrowserTool as _SimpleBrowserTool
except ImportError:
    _BrowserTool = _SimpleBrowserTool = None

try:
    from .utils.web_crawler import WebCrawlerTool as _WebCrawlerTool, SimpleWebScraperTool as _SimpleWebScraperTool
except ImportError:
    _WebCrawlerTool = _SimpleWebScraperTool = None

try:
    from .utils.chat_completion import ChatCompletionTool as _ChatCompletionTool, SimplePromptTool as _SimplePromptTool
except ImportError:
    _ChatCompletionTool = _SimplePromptTool = None

try:
    from .utils.vnc import VNCComputerUseTool as _VNCComputerUseTool, SimpleVNCComputerUseTool as _SimpleVNCComputerUseTool
except ImportError:
    _VNCComputerUseTool = _SimpleVNCComputerUseTool = None

try:
    from .utils.macos import MacOSUseTool as _MacOSUseTool, SimpleMacOSTool as _SimpleMacOSTool
except ImportError:
    _MacOSUseTool = _SimpleMacOSTool = None

# Create wrapper functions with @tool decorator for core tools

@tool
def bash_tool(command: str, restart: bool = False) -> str:
    """
    Execute bash commands in the terminal.
    
    Args:
        command: The bash command to execute. Can be empty to view additional logs when previous exit code is `-1`. Can be `ctrl+c` to interrupt the currently running process.
        restart: Whether to restart the bash session
    
    Returns:
        Command output or error message
    """
    tool_instance = _BashTool()
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(tool_instance.execute(command=command, restart=restart))
    except RuntimeError:
        result = asyncio.run(tool_instance.execute(command=command, restart=restart))
    
    if result.success:
        return result.output
    else:
        return f"Error: {result.error}"

@tool
def python_executor(code: str, timeout: int = 30) -> str:
    """
    Execute Python code with timeout and safety restrictions.
    
    Args:
        code: The Python code to execute
        timeout: Execution timeout in seconds (default: 30)
    
    Returns:
        Execution output or error message
    """
    tool_instance = _PythonExecutorTool()
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(tool_instance.execute(code=code, timeout=timeout))
    except RuntimeError:
        result = asyncio.run(tool_instance.execute(code=code, timeout=timeout))
    
    if result.success:
        return result.output
    else:
        return f"Error: {result.error}"

@tool
def safe_python_executor(code: str, timeout: int = 30) -> str:
    """
    Execute Python code with enhanced safety restrictions.
    
    Args:
        code: The Python code to execute
        timeout: Execution timeout in seconds (default: 30)
    
    Returns:
        Execution output or error message
    """
    tool_instance = _SafePythonExecutorTool()
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(tool_instance.execute(code=code, timeout=timeout))
    except RuntimeError:
        result = asyncio.run(tool_instance.execute(code=code, timeout=timeout))
    
    if result.success:
        return result.output
    else:
        return f"Error: {result.error}"

@tool
def file_editor(command: str, path: str, file_text: str = None, old_str: str = None, new_str: str = None, view_range: str = None) -> str:
    """
    Edit files with various operations like create, read, write, and str_replace.
    
    Args:
        command: The command to execute (view, create, str_replace, undo_edit)
        path: Absolute path to file
        file_text: Text content to write to file (for 'create' command)
        old_str: String to be replaced (for 'str_replace' command)
        new_str: String to replace with (for 'str_replace' command)
        view_range: Range of lines to view, e.g., '[1, 50]' (for 'view' command)
    
    Returns:
        Operation result or error message
    """
    tool_instance = _FileEditorTool()
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(tool_instance.execute(
            command=command, path=path, file_text=file_text,
            old_str=old_str, new_str=new_str, view_range=view_range
        ))
    except RuntimeError:
        result = asyncio.run(tool_instance.execute(
            command=command, path=path, file_text=file_text,
            old_str=old_str, new_str=new_str, view_range=view_range
        ))
    
    if result.success:
        return result.output
    else:
        return f"Error: {result.error}"

@tool
def file_reader(path: str) -> str:
    """
    Read the contents of a file.
    
    Args:
        path: Path to the file to read
    
    Returns:
        File contents or error message
    """
    tool_instance = _SimpleFileReaderTool()
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(tool_instance.execute(path=path))
    except RuntimeError:
        result = asyncio.run(tool_instance.execute(path=path))
    
    if result.success:
        return result.output
    else:
        return f"Error: {result.error}"

@tool
def file_writer(path: str, content: str) -> str:
    """
    Write content to a file.
    
    Args:
        path: Path to the file to write
        content: Content to write to the file
    
    Returns:
        Success message or error message
    """
    tool_instance = _SimpleFileWriterTool()
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(tool_instance.execute(path=path, content=content))
    except RuntimeError:
        result = asyncio.run(tool_instance.execute(path=path, content=content))
    
    if result.success:
        return result.output
    else:
        return f"Error: {result.error}"

@tool
def planning_tool(action: str, task_description: str = None, plan_id: str = None, task_id: str = None,
                  subtask_title: str = None, subtask_description: str = None, priority: str = "medium",
                  estimated_time: str = None, dependencies: str = None, update_content: str = None) -> str:
    """
    Create and manage task plans and workflows.
    
    Args:
        action: Action to perform (create_plan, add_task, update_task, complete_task, get_plan, analyze_task)
        task_description: Description of the main task or goal
        plan_id: ID of the plan to work with
        task_id: ID of specific task within plan
        subtask_title: Title for new subtask
        subtask_description: Description for new subtask
        priority: Priority level (high, medium, low)
        estimated_time: Estimated time to complete
        dependencies: Comma-separated list of task IDs this task depends on
        update_content: Content to update task with
    
    Returns:
        Planning operation result or error message
    """
    tool_instance = _PlanningTool()
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(tool_instance.execute(
            action=action, task_description=task_description, plan_id=plan_id, task_id=task_id,
            subtask_title=subtask_title, subtask_description=subtask_description, priority=priority,
            estimated_time=estimated_time, dependencies=dependencies, update_content=update_content
        ))
    except RuntimeError:
        result = asyncio.run(tool_instance.execute(
            action=action, task_description=task_description, plan_id=plan_id, task_id=task_id,
            subtask_title=subtask_title, subtask_description=subtask_description, priority=priority,
            estimated_time=estimated_time, dependencies=dependencies, update_content=update_content
        ))
    
    if result.success:
        return result.output
    else:
        return f"Error: {result.error}"

# Export the original tool classes for backward compatibility (without @tool decorator)
# These can be used directly as smolagents Tool classes
BashTool = _BashTool
PythonExecutorTool = _PythonExecutorTool
SafePythonExecutorTool = _SafePythonExecutorTool
FileEditorTool = _FileEditorTool
SimpleFileReaderTool = _SimpleFileReaderTool
SimpleFileWriterTool = _SimpleFileWriterTool
PlanningTool = _PlanningTool

WebSearchTool = _WebSearchTool
DuckDuckGoSearchTool = _DuckDuckGoSearchTool
GoogleSearchTool = _GoogleSearchTool
BingSearchTool = _BingSearchTool

BrowserTool = _BrowserTool
SimpleBrowserTool = _SimpleBrowserTool

WebCrawlerTool = _WebCrawlerTool
SimpleWebScraperTool = _SimpleWebScraperTool

ChatCompletionTool = _ChatCompletionTool
SimplePromptTool = _SimplePromptTool

VNCComputerUseTool = _VNCComputerUseTool
SimpleVNCComputerUseTool = _SimpleVNCComputerUseTool

MacOSUseTool = _MacOSUseTool
SimpleMacOSTool = _SimpleMacOSTool