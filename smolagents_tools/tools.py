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
def python_executor_tool(code: str, timeout: int = 30) -> str:
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
def safe_python_executor_tool(code: str, timeout: int = 30) -> str:
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
def file_editor_tool(command: str, path: str, file_text: str = None, old_str: str = None, new_str: str = None, view_range: str = None) -> str:
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
def file_reader_tool(path: str) -> str:
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
def file_writer_tool(path: str, content: str) -> str:
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

# Optional tools with @tool decorators (only if available)

if _WebSearchTool:
    @tool
    def web_search_tool(query: str, engine: str = "duckduckgo", max_results: int = 10, region: str = "us-en", time_range: str = None) -> str:
        """
        Search the web using various search engines.
        
        Args:
            query: The search query
            engine: Search engine to use (duckduckgo, google, bing)
            max_results: Maximum number of results to return
            region: Region for search results (e.g., 'us-en', 'uk-en')
            time_range: Time range for results (d, w, m, y)
        
        Returns:
            Search results or error message
        """
        tool_instance = _WebSearchTool()
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(tool_instance.execute(
                query=query, engine=engine, max_results=max_results,
                region=region, time_range=time_range
            ))
        except RuntimeError:
            result = asyncio.run(tool_instance.execute(
                query=query, engine=engine, max_results=max_results,
                region=region, time_range=time_range
            ))
        
        if result.success:
            return result.output
        else:
            return f"Error: {result.error}"

if _BrowserTool:
    @tool
    def browser_tool(action: str, url: str = None, selector: str = None, text: str = None,
                     wait_time: int = 1000, scroll_direction: str = "down", headless: bool = True) -> str:
        """
        Automate browser interactions using Playwright.
        
        Args:
            action: Action to perform (navigate, screenshot, click, fill, extract_text, scroll, wait, close)
            url: URL to navigate to (required for 'navigate' action)
            selector: CSS selector for element (required for click, fill, extract_text actions)
            text: Text to fill in form field (required for 'fill' action)
            wait_time: Time to wait in milliseconds (for 'wait' action)
            scroll_direction: Direction to scroll (up, down, left, right)
            headless: Run browser in headless mode
        
        Returns:
            Browser operation result or error message
        """
        tool_instance = _BrowserTool()
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(tool_instance.execute(
                action=action, url=url, selector=selector, text=text,
                wait_time=wait_time, scroll_direction=scroll_direction, headless=headless
            ))
        except RuntimeError:
            result = asyncio.run(tool_instance.execute(
                action=action, url=url, selector=selector, text=text,
                wait_time=wait_time, scroll_direction=scroll_direction, headless=headless
            ))
        
        if result.success:
            return result.output
        else:
            return f"Error: {result.error}"

if _WebCrawlerTool:
    @tool
    def web_crawler_tool(url: str, extraction_strategy: str = "basic", css_selector: str = None,
                    word_count_threshold: int = 10, only_text: bool = True,
                    include_links: bool = False, include_images: bool = False) -> str:
        """
        Crawl web pages and extract structured content.
        
        Args:
            url: URL to crawl
            extraction_strategy: Strategy to use (basic, llm, css, xpath)
            css_selector: CSS selector for targeted extraction (when using css strategy)
            word_count_threshold: Minimum word count for content blocks
            only_text: Extract only text content
            include_links: Include links in extraction
            include_images: Include images in extraction
        
        Returns:
            Crawled content or error message
        """
        tool_instance = _WebCrawlerTool()
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(tool_instance.execute(
                url=url, extraction_strategy=extraction_strategy, css_selector=css_selector,
                word_count_threshold=word_count_threshold, only_text=only_text,
                include_links=include_links, include_images=include_images
            ))
        except RuntimeError:
            result = asyncio.run(tool_instance.execute(
                url=url, extraction_strategy=extraction_strategy, css_selector=css_selector,
                word_count_threshold=word_count_threshold, only_text=only_text,
                include_links=include_links, include_images=include_images
            ))
        
        if result.success:
            return result.output
        else:
            return f"Error: {result.error}"

if _ChatCompletionTool:
    @tool
    def chat_completion_tool(messages: str, provider: str = "openai", model: str = "gpt-3.5-turbo",
                       temperature: float = 0.7, max_tokens: int = 1000, system_prompt: str = None,
                       api_key: str = None, region: str = "us-east-1") -> str:
        """
        Generate chat completions using various LLM providers.
        
        Args:
            messages: JSON string of messages array or single message string
            provider: LLM provider (openai, anthropic, bedrock, local)
            model: Model name
            temperature: Response temperature (0.0 to 2.0)
            max_tokens: Maximum tokens in response
            system_prompt: System prompt to set context
            api_key: API key for the provider
            region: AWS region for Bedrock
        
        Returns:
            Generated completion or error message
        """
        tool_instance = _ChatCompletionTool()
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(tool_instance.execute(
                messages=messages, provider=provider, model=model, temperature=temperature,
                max_tokens=max_tokens, system_prompt=system_prompt, api_key=api_key, region=region
            ))
        except RuntimeError:
            result = asyncio.run(tool_instance.execute(
                messages=messages, provider=provider, model=model, temperature=temperature,
                max_tokens=max_tokens, system_prompt=system_prompt, api_key=api_key, region=region
            ))
        
        if result.success:
            return result.output
        else:
            return f"Error: {result.error}"

if _VNCComputerUseTool:
    @tool
    def vnc_tool(action: str, host: str = None, port: int = 5900, password: str = None,
                 x: int = None, y: int = None, button: int = 1, key: str = None,
                 text: str = None, filename: str = None, timeout: float = 15) -> str:
        """
        Automate VNC sessions for remote computer control.
        
        Args:
            action: Action to perform (connect, disconnect, mouse_move, mouse_click, key_press, type_text, capture_screen)
            host: VNC server host (required for 'connect' action)
            port: VNC server port (default: 5900)
            password: VNC server password
            x: X coordinate for mouse actions
            y: Y coordinate for mouse actions
            button: Mouse button (1=left, 2=middle, 3=right)
            key: Key to press (supports combinations like 'lctrl-c')
            text: Text to type
            filename: Filename for screen capture
            timeout: Timeout for the VNC operation in seconds
        
        Returns:
            VNC operation result or error message
        """
        tool_instance = _VNCComputerUseTool()
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(tool_instance.execute(
                action=action, host=host, port=port, password=password,
                x=x, y=y, button=button, key=key, text=text, filename=filename, timeout=timeout
            ))
        except RuntimeError:
            result = asyncio.run(tool_instance.execute(
                action=action, host=host, port=port, password=password,
                x=x, y=y, button=button, key=key, text=text, filename=filename, timeout=timeout
            ))
        
        if result.success:
            return result.output
        else:
            return f"Error: {result.error}"

if _MacOSUseTool:
    @tool
    def macos_tool(action: str, app_name: str = None, element_index: int = None, text: str = None,
                   submit: bool = False, click_action: str = "AXPress", scroll_direction: str = "down",
                   script: str = None) -> str:
        """
        Automate macOS applications and system interactions.
        
        Args:
            action: Action to perform (open_app, get_ui_tree, click_element, input_text, right_click, scroll, run_applescript, screenshot, close)
            app_name: Name of the app to open
            element_index: Index of UI element to interact with
            text: Text to input
            submit: Whether to submit after text input
            click_action: Type of click action (AXPress, AXClick, AXOpen, AXConfirm, AXShowMenu)
            scroll_direction: Direction to scroll (up, down, left, right)
            script: AppleScript code to execute
        
        Returns:
            macOS operation result or error message
        """
        tool_instance = _MacOSUseTool()
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(tool_instance.execute(
                action=action, app_name=app_name, element_index=element_index, text=text,
                submit=submit, click_action=click_action, scroll_direction=scroll_direction, script=script
            ))
        except RuntimeError:
            result = asyncio.run(tool_instance.execute(
                action=action, app_name=app_name, element_index=element_index, text=text,
                submit=submit, click_action=click_action, scroll_direction=scroll_direction, script=script
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