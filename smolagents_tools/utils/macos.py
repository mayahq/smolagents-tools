"""
macOS automation tool adapted for smolagents
Based on the macOS-use library (mlx-use)
"""

import asyncio
import logging
import subprocess
from typing import Optional, Dict, Any, List
from .base import AsyncSmolTool, SmolToolResult

# Import macOS-use components
try:
    from mlx_use import Agent, Controller
    from mlx_use.agent.views import ActionResult
    from mlx_use.mac.tree import MacUITreeBuilder
    MACOS_USE_AVAILABLE = True
except ImportError as e:
    MACOS_USE_AVAILABLE = False
    _import_error = str(e)

# Import Cocoa separately as it might not be available on non-macOS systems
try:
    import Cocoa
    COCOA_AVAILABLE = True
except ImportError:
    COCOA_AVAILABLE = False

logger = logging.getLogger(__name__)


class MacOSUseTool(AsyncSmolTool):
    """
    A tool for macOS automation using the mlx-use library
    Provides UI element interaction, app launching, and AppleScript execution
    """
    
    def __init__(self):
        self.name = "macos"
        self.description = """A tool for macOS automation. Can open apps, interact with UI elements, take screenshots, run AppleScript, and automate macOS applications."""
        
        self.inputs = {
            "action": {
                "type": "string",
                "description": "Action to perform: open_app, get_ui_tree, click_element, input_text, right_click, scroll, run_applescript, screenshot, close",
                "required": True
            },
            "app_name": {
                "type": "string",
                "description": "Name of the app to open (required for 'open_app' action)",
                "required": False
            },
            "element_index": {
                "type": "integer",
                "description": "Index of UI element to interact with (required for click_element, input_text, right_click, scroll actions)",
                "required": False
            },
            "text": {
                "type": "string",
                "description": "Text to input (required for 'input_text' action)",
                "required": False
            },
            "submit": {
                "type": "boolean",
                "description": "Whether to submit after text input (for 'input_text' action)",
                "default": False,
                "required": False
            },
            "click_action": {
                "type": "string",
                "description": "Type of click action: AXPress, AXClick, AXOpen, AXConfirm, AXShowMenu (for 'click_element' action)",
                "default": "AXPress",
                "required": False
            },
            "scroll_direction": {
                "type": "string",
                "description": "Direction to scroll: up, down, left, right (for 'scroll' action)",
                "default": "down",
                "required": False
            },
            "script": {
                "type": "string",
                "description": "AppleScript code to execute (required for 'run_applescript' action)",
                "required": False
            }
        }
        self.output_type = "string"
        
        self._controller: Optional[Controller] = None
        self._mac_tree_builder: Optional[MacUITreeBuilder] = None
        self._current_app_pid: Optional[int] = None
        super().__init__()
    
    def _ensure_controller(self) -> None:
        """Ensure controller is initialized"""
        if not MACOS_USE_AVAILABLE:
            return
        if self._controller is None:
            self._controller = Controller()
            self._mac_tree_builder = MacUITreeBuilder()
    
    async def _open_app(self, app_name: str) -> SmolToolResult:
        """Open a macOS application"""
        try:
            if MACOS_USE_AVAILABLE:
                self._ensure_controller()
                # Try to use mlx-use if available
                try:
                    result = await self._controller.registry.execute_action(
                        "open_app", 
                        {"app_name": app_name}
                    )
                    
                    if isinstance(result, ActionResult):
                        if result.error:
                            # Fall back to AppleScript
                            return await self._open_app_applescript(app_name)
                        else:
                            self._current_app_pid = getattr(result, 'current_app_pid', None)
                            return SmolToolResult(
                                output=f"Successfully opened {app_name}. PID: {self._current_app_pid}",
                                success=True
                            )
                    else:
                        return await self._open_app_applescript(app_name)
                except Exception:
                    return await self._open_app_applescript(app_name)
            else:
                return await self._open_app_applescript(app_name)
                
        except Exception as e:
            return SmolToolResult(
                error=f"Failed to open app {app_name}: {str(e)}",
                success=False
            )
    
    async def _open_app_applescript(self, app_name: str) -> SmolToolResult:
        """Open app using AppleScript fallback"""
        try:
            script = f'tell application "{app_name}" to activate'
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return SmolToolResult(
                    output=f"Opened app '{app_name}' successfully using AppleScript",
                    success=True
                )
            else:
                return SmolToolResult(
                    error=f"Failed to open app '{app_name}': {result.stderr}",
                    success=False
                )
        except Exception as e:
            return SmolToolResult(
                error=f"Failed to open app '{app_name}': {str(e)}",
                success=False
            )
    
    async def _get_ui_tree(self) -> SmolToolResult:
        """Get the current UI tree of the active application"""
        try:
            if not MACOS_USE_AVAILABLE:
                return SmolToolResult(
                    error="UI tree functionality requires mlx-use library. Please install with: pip install mlx-use",
                    success=False
                )
            
            self._ensure_controller()
            
            if not self._current_app_pid:
                return SmolToolResult(
                    error="No app is currently open. Use 'open_app' action first.",
                    success=False
                )
            
            # Build UI tree
            root = await self._mac_tree_builder.build_tree(self._current_app_pid)
            if root:
                ui_tree_string = root.get_clickable_elements_string()
                return SmolToolResult(
                    output=f"UI Tree for PID {self._current_app_pid}:\n{ui_tree_string}",
                    success=True
                )
            else:
                return SmolToolResult(
                    error="Failed to build UI tree. App may have been closed.",
                    success=False
                )
                
        except Exception as e:
            return SmolToolResult(
                error=f"Failed to get UI tree: {str(e)}",
                success=False
            )
    
    async def _click_element(self, element_index: int, click_action: str = "AXPress") -> SmolToolResult:
        """Click a UI element by index"""
        try:
            if not MACOS_USE_AVAILABLE:
                return SmolToolResult(
                    error="Element clicking requires mlx-use library. Please install with: pip install mlx-use",
                    success=False
                )
            
            self._ensure_controller()
            
            result = await self._controller.registry.execute_action(
                "click_element",
                {"index": element_index, "action": click_action},
                mac_tree_builder=self._mac_tree_builder
            )
            
            if isinstance(result, ActionResult):
                if result.error:
                    return SmolToolResult(
                        error=f"Failed to click element {element_index}: {result.error}",
                        success=False
                    )
                else:
                    return SmolToolResult(
                        output=f"Successfully clicked element {element_index}",
                        success=True
                    )
            else:
                return SmolToolResult(
                    error=f"Unexpected result type from click_element: {type(result)}",
                    success=False
                )
                
        except Exception as e:
            return SmolToolResult(
                error=f"Failed to click element {element_index}: {str(e)}",
                success=False
            )
    
    async def _input_text(self, element_index: int, text: str, submit: bool = False) -> SmolToolResult:
        """Input text into a UI element"""
        try:
            if not MACOS_USE_AVAILABLE:
                return SmolToolResult(
                    error="Text input requires mlx-use library. Please install with: pip install mlx-use",
                    success=False
                )
            
            self._ensure_controller()
            
            result = await self._controller.registry.execute_action(
                "input_text",
                {"index": element_index, "text": text, "submit": submit},
                mac_tree_builder=self._mac_tree_builder
            )
            
            if isinstance(result, ActionResult):
                if result.error:
                    return SmolToolResult(
                        error=f"Failed to input text into element {element_index}: {result.error}",
                        success=False
                    )
                else:
                    return SmolToolResult(
                        output=f"Successfully input text into element {element_index}",
                        success=True
                    )
            else:
                return SmolToolResult(
                    error=f"Unexpected result type from input_text: {type(result)}",
                    success=False
                )
                
        except Exception as e:
            return SmolToolResult(
                error=f"Failed to input text into element {element_index}: {str(e)}",
                success=False
            )
    
    async def _right_click_element(self, element_index: int) -> SmolToolResult:
        """Right-click a UI element"""
        try:
            if not MACOS_USE_AVAILABLE:
                return SmolToolResult(
                    error="Right-click requires mlx-use library. Please install with: pip install mlx-use",
                    success=False
                )
            
            self._ensure_controller()
            
            # Use the controller's right_click_element action if available
            try:
                result = await self._controller.registry.execute_action(
                    "right_click_element",
                    {"index": element_index},
                    mac_tree_builder=self._mac_tree_builder
                )
            except Exception:
                # Fallback: try to use click with AXShowMenu action
                result = await self._controller.registry.execute_action(
                    "click_element",
                    {"index": element_index, "action": "AXShowMenu"},
                    mac_tree_builder=self._mac_tree_builder
                )
            
            if isinstance(result, ActionResult):
                if result.error:
                    return SmolToolResult(
                        error=f"Failed to right-click element {element_index}: {result.error}",
                        success=False
                    )
                else:
                    return SmolToolResult(
                        output=f"Successfully right-clicked element {element_index}",
                        success=True
                    )
            else:
                return SmolToolResult(
                    error=f"Unexpected result type from right_click_element: {type(result)}",
                    success=False
                )
                
        except Exception as e:
            return SmolToolResult(
                error=f"Failed to right-click element {element_index}: {str(e)}",
                success=False
            )
    
    async def _scroll_element(self, element_index: int, direction: str = "down") -> SmolToolResult:
        """Scroll a UI element"""
        try:
            if not MACOS_USE_AVAILABLE:
                return SmolToolResult(
                    error="Scrolling requires mlx-use library. Please install with: pip install mlx-use",
                    success=False
                )
            
            self._ensure_controller()
            
            # Use the controller's scroll_element action if available
            try:
                result = await self._controller.registry.execute_action(
                    "scroll_element",
                    {"index": element_index, "direction": direction},
                    mac_tree_builder=self._mac_tree_builder
                )
            except Exception:
                # Fallback: return error message
                return SmolToolResult(
                    error=f"Scroll functionality not available in current mlx-use version",
                    success=False
                )
            
            if isinstance(result, ActionResult):
                if result.error:
                    return SmolToolResult(
                        error=f"Failed to scroll element {element_index}: {result.error}",
                        success=False
                    )
                else:
                    return SmolToolResult(
                        output=f"Successfully scrolled element {element_index} {direction}",
                        success=True
                    )
            else:
                return SmolToolResult(
                    error=f"Unexpected result type from scroll_element: {type(result)}",
                    success=False
                )
                
        except Exception as e:
            return SmolToolResult(
                error=f"Failed to scroll element {element_index}: {str(e)}",
                success=False
            )
    
    async def _run_applescript(self, script: str) -> SmolToolResult:
        """Execute AppleScript code"""
        try:
            if MACOS_USE_AVAILABLE:
                self._ensure_controller()
                try:
                    result = await self._controller.registry.execute_action(
                        "run_apple_script",
                        {"script": script}
                    )
                    
                    if isinstance(result, ActionResult):
                        if result.error:
                            # Fall back to subprocess
                            return await self._run_applescript_subprocess(script)
                        else:
                            return SmolToolResult(
                                output=f"AppleScript executed successfully: {result.extracted_content}",
                                success=True
                            )
                    else:
                        return await self._run_applescript_subprocess(script)
                except Exception:
                    return await self._run_applescript_subprocess(script)
            else:
                return await self._run_applescript_subprocess(script)
                
        except Exception as e:
            return SmolToolResult(
                error=f"Failed to execute AppleScript: {str(e)}",
                success=False
            )
    
    async def _run_applescript_subprocess(self, script: str) -> SmolToolResult:
        """Execute AppleScript using subprocess fallback"""
        try:
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return SmolToolResult(
                    output=f"AppleScript executed successfully: {result.stdout.strip()}",
                    success=True
                )
            else:
                return SmolToolResult(
                    error=f"AppleScript failed: {result.stderr}",
                    success=False
                )
        except Exception as e:
            return SmolToolResult(
                error=f"AppleScript failed: {str(e)}",
                success=False
            )
    
    async def _screenshot(self) -> SmolToolResult:
        """Take a screenshot of the current screen"""
        try:
            # Use AppleScript to take a screenshot
            script = '''
            set screenshotPath to (path to desktop as string) & "screenshot_" & (current date) & ".png"
            do shell script "screencapture -x " & quoted form of POSIX path of screenshotPath
            return POSIX path of screenshotPath
            '''
            
            result = await self._run_applescript(script)
            if result.success:
                return SmolToolResult(
                    output=f"Screenshot saved: {result.output}",
                    success=True
                )
            else:
                return result
                
        except Exception as e:
            return SmolToolResult(
                error=f"Failed to take screenshot: {str(e)}",
                success=False
            )
    
    async def _close(self) -> SmolToolResult:
        """Close the current session and cleanup"""
        try:
            if self._mac_tree_builder:
                if hasattr(self._mac_tree_builder, 'cleanup'):
                    self._mac_tree_builder.cleanup()
                self._mac_tree_builder = None
            
            self._controller = None
            self._current_app_pid = None
            
            return SmolToolResult(
                output="macOS session closed successfully",
                success=True
            )
            
        except Exception as e:
            return SmolToolResult(
                error=f"Failed to close session: {str(e)}",
                success=False
            )
    
    async def execute(self, action: str, app_name: str = None, element_index: int = None,
                     text: str = None, submit: bool = False, click_action: str = "AXPress",
                     scroll_direction: str = "down", script: str = None, **kwargs) -> SmolToolResult:
        """
        Execute macOS automation action.
        
        Args:
            action (str): Action to perform
            app_name (str): App name for open_app action
            element_index (int): Element index for UI interactions
            text (str): Text for input_text action
            submit (bool): Whether to submit after text input
            click_action (str): Type of click action
            scroll_direction (str): Scroll direction
            script (str): AppleScript code
            
        Returns:
            SmolToolResult: Result of the macOS operation
        """
        try:
            if action == "open_app":
                if not app_name:
                    return SmolToolResult(
                        error="app_name is required for open_app action",
                        success=False
                    )
                return await self._open_app(app_name)
            
            elif action == "get_ui_tree":
                return await self._get_ui_tree()
            
            elif action == "click_element":
                if element_index is None:
                    return SmolToolResult(
                        error="element_index is required for click_element action",
                        success=False
                    )
                return await self._click_element(element_index, click_action)
            
            elif action == "input_text":
                if element_index is None or not text:
                    return SmolToolResult(
                        error="element_index and text are required for input_text action",
                        success=False
                    )
                return await self._input_text(element_index, text, submit)
            
            elif action == "right_click":
                if element_index is None:
                    return SmolToolResult(
                        error="element_index is required for right_click action",
                        success=False
                    )
                return await self._right_click_element(element_index)
            
            elif action == "scroll":
                if element_index is None:
                    return SmolToolResult(
                        error="element_index is required for scroll action",
                        success=False
                    )
                return await self._scroll_element(element_index, scroll_direction)
            
            elif action == "run_applescript":
                if not script:
                    return SmolToolResult(
                        error="script is required for run_applescript action",
                        success=False
                    )
                return await self._run_applescript(script)
            
            elif action == "screenshot":
                return await self._screenshot()
            
            elif action == "close":
                return await self._close()
            
            else:
                return SmolToolResult(
                    error=f"Unknown action: {action}",
                    success=False
                )
                
        except Exception as e:
            return SmolToolResult(
                error=f"macOS tool error: {str(e)}",
                success=False
            )
    
    async def __aenter__(self):
        """Async context manager entry"""
        if MACOS_USE_AVAILABLE:
            self._ensure_controller()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._close()


class SimpleMacOSTool(AsyncSmolTool):
    """Simplified macOS tool for basic operations"""
    
    def __init__(self):
        self.name = "simple_macos"
        self.description = """A simplified macOS automation tool that works without mlx-use. Provides basic app launching and AppleScript execution."""
        
        self.inputs = {
            "action": {
                "type": "string",
                "description": "Action to perform: open_app, run_applescript",
                "required": True
            },
            "app_name": {
                "type": "string",
                "description": "Name of the app to open (required for 'open_app' action)",
                "required": False
            },
            "script": {
                "type": "string",
                "description": "AppleScript code to execute (required for 'run_applescript' action)",
                "required": False
            }
        }
        self.output_type = "string"
        super().__init__()
    
    async def execute(self, action: str, app_name: str = None, script: str = None, 
                     **kwargs) -> SmolToolResult:
        """Execute simple macOS operation"""
        
        try:
            if action == "open_app":
                if not app_name:
                    return SmolToolResult(
                        error="app_name is required for open_app action",
                        success=False
                    )
                
                try:
                    applescript = f'tell application "{app_name}" to activate'
                    result = subprocess.run(['osascript', '-e', applescript], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        return SmolToolResult(
                            output=f"Successfully opened {app_name}",
                            success=True
                        )
                    else:
                        return SmolToolResult(
                            error=f"Failed to open {app_name}: {result.stderr}",
                            success=False
                        )
                except Exception as e:
                    return SmolToolResult(
                        error=f"Failed to open {app_name}: {str(e)}",
                        success=False
                    )
            
            elif action == "run_applescript":
                if not script:
                    return SmolToolResult(
                        error="script is required for run_applescript action",
                        success=False
                    )
                
                try:
                    result = subprocess.run(['osascript', '-e', script], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        return SmolToolResult(
                            output=f"AppleScript executed successfully: {result.stdout.strip()}",
                            success=True
                        )
                    else:
                        return SmolToolResult(
                            error=f"AppleScript failed: {result.stderr}",
                            success=False
                        )
                except Exception as e:
                    return SmolToolResult(
                        error=f"AppleScript execution failed: {str(e)}",
                        success=False
                    )
            
            else:
                return SmolToolResult(
                    error=f"Unknown action: {action}. Available actions: open_app, run_applescript",
                    success=False
                )
                
        except Exception as e:
            return SmolToolResult(
                error=f"Simple macOS tool error: {str(e)}",
                success=False
            )