"""
VNC Computer Use Tool for smolagents
Provides automation capabilities for VNC servers using vncdotool command-line interface
FIXED VERSION: Uses command-line vncdotool to avoid Python SDK hanging issues
"""

import asyncio
import logging
import subprocess
from typing import Optional, Dict, Any
from .base import AsyncSmolTool, SmolToolResult
import base64

logger = logging.getLogger(__name__)


import json
import os

# File to persist VNC connection state across Python processes
VNC_STATE_FILE = '/tmp/vnc_connection_state.json'

def _load_vnc_state():
    """Load VNC connection state from file"""
    try:
        if os.path.exists(VNC_STATE_FILE):
            with open(VNC_STATE_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return {
        'connected_host': None,
        'connection_string': None,
        'password': None
    }

def _save_vnc_state(state):
    """Save VNC connection state to file"""
    try:
        with open(VNC_STATE_FILE, 'w') as f:
            json.dump(state, f)
    except Exception:
        pass

# Global connection state to persist across tool instances
_global_vnc_state = _load_vnc_state()

class VNCComputerUseTool(AsyncSmolTool):
    """
    A tool for VNC automation using vncdotool command-line interface
    Provides mouse, keyboard control and screen capture capabilities for VNC sessions
    FIXED: Uses command-line vncdotool to avoid Twisted reactor conflicts and hanging issues
    FIXED: Uses global connection state to persist across tool instances
    """
    
    def __init__(self):
        self.name = "vnc_computer"
        self.description = """A tool for VNC automation using reliable command-line vncdotool. Can control mouse, keyboard, and capture screenshots from VNC sessions.

SUPPORTED KEY MAPPINGS:
- Special keys: bsp, tab, return/enter, esc, ins, delete/del, home, end, pgup, pgdn
- Arrow keys: left, up, right, down
- Function keys: f1-f20
- Modifiers: lshift/shift, rshift, lctrl/ctrl, rctrl, lalt/alt, ralt, lmeta/meta, rmeta
- System keys: scrlk, sysrq, numlk, caplk, pause, lsuper/super, rsuper, lhyper/hyper, rhyper
- Keypad: kp0-kp9, kpenter
- Other: slash, bslash, fslash, spacebar/space/sb

KEY COMBINATIONS:
Use hyphens to combine keys: 'lctrl-c' (Ctrl+C), 'lalt-f2' (Alt+F2), 'lctrl-lalt-del' (Ctrl+Alt+Del)

EXAMPLES:
- Open run dialog: key='lalt-f2'
- Copy: key='lctrl-c'
- Paste: key='lctrl-v'
- Save: key='lctrl-s'
- Ctrl+Alt+Del: key='lctrl-lalt-del'
"""
        
        self.inputs = {
            "action": {
                "type": "string",
                "description": "Action to perform: connect, disconnect, mouse_move, mouse_click, key_press, type_text, capture_screen, capture_region",
                "required": True
            },
            "host": {
                "type": "string",
                "description": "VNC server host (required for 'connect' action)",
                "required": False
            },
            "port": {
                "type": "integer",
                "description": "VNC server port (default: 5900)",
                "default": 5900,
                "required": False
            },
            "password": {
                "type": "string",
                "description": "VNC server password (optional)",
                "required": False
            },
            "x": {
                "type": "integer",
                "description": "X coordinate for mouse actions",
                "required": False
            },
            "y": {
                "type": "integer",
                "description": "Y coordinate for mouse actions",
                "required": False
            },
            "button": {
                "type": "integer",
                "description": "Mouse button (1=left, 2=middle, 3=right)",
                "default": 1,
                "required": False
            },
            "key": {
                "type": "string",
                "description": "Key to press (required for 'key_press' action). Supports single keys and combinations with hyphens. Examples: 'return', 'lalt-f2', 'lctrl-c', 'lctrl-lalt-del'. See tool description for full keymap.",
                "required": False
            },
            "text": {
                "type": "string",
                "description": "Text to type (required for 'type_text' action)",
                "required": False
            },
            "filename": {
                "type": "string",
                "description": "Filename for screen capture (required for 'capture_screen' and 'capture_region' actions)",
                "required": False
            },
            "width": {
                "type": "integer",
                "description": "Width for region capture",
                "required": False
            },
            "height": {
                "type": "integer",
                "description": "Height for region capture",
                "required": False
            },
            "timeout": {
                "type": "number",
                "description": "Timeout for the VNC operation in seconds (default: 15)",
                "default": 15,
                "required": False
            },
            "img_title": {
                "type": "string",
                "description": "Title attribute for the base64 image tag (used with capture_screen and capture_region)",
                "default": "VNC Screenshot",
                "required": False
            },
            "img_alt": {
                "type": "string",
                "description": "Alt text for the base64 image tag (used with capture_screen and capture_region)",
                "default": "VNC screen capture",
                "required": False
            },
            "display": {
                "type": "string",
                "description": "Whether to display the screenshot (used with capture_screen and capture_region)",
                "default": "true",
                "required": False
            },
            "include_in_next_call": {
                "type": "string",
                "description": "Whether to include screenshot in next agent call (used with capture_screen and capture_region)",
                "default": "true",
                "required": False
            }
        }
        self.output_type = "string"
        super().__init__()
    
    @property
    def _connected_host(self):
        # Reload state from file to get latest updates
        global _global_vnc_state
        _global_vnc_state = _load_vnc_state()
        return _global_vnc_state['connected_host']
    
    @_connected_host.setter
    def _connected_host(self, value):
        global _global_vnc_state
        _global_vnc_state['connected_host'] = value
        _save_vnc_state(_global_vnc_state)
    
    @property
    def _connection_string(self):
        # Reload state from file to get latest updates
        global _global_vnc_state
        _global_vnc_state = _load_vnc_state()
        return _global_vnc_state['connection_string']
    
    @_connection_string.setter
    def _connection_string(self, value):
        global _global_vnc_state
        _global_vnc_state['connection_string'] = value
        _save_vnc_state(_global_vnc_state)
    
    @property
    def _password(self):
        # Reload state from file to get latest updates
        global _global_vnc_state
        _global_vnc_state = _load_vnc_state()
        return _global_vnc_state['password']
    
    @_password.setter
    def _password(self, value):
        global _global_vnc_state
        _global_vnc_state['password'] = value
        _save_vnc_state(_global_vnc_state)
    
    def _build_connection_string(self, host: str, port: int) -> str:
        """Build VNC connection string for vncdotool command-line"""
        if port == 5900:
            return host
        elif port > 5900:
            display_num = port - 5900
            return f"{host}:{display_num}"
        else:
            return f"{host}::{port}"
    
    async def _execute_vnc_command(self, command_args: list, timeout: float = 15) -> SmolToolResult:
        """Execute vncdotool command-line with proper error handling"""
        try:
            if not self._connection_string:
                return SmolToolResult(
                    error="Not connected to VNC server. Use 'connect' action first.",
                    success=False
                )
            
            # Build base command
            base_cmd = ["vncdotool", "-s", self._connection_string]
            if self._password:
                base_cmd.extend(["-p", self._password])
            
            full_cmd = base_cmd + command_args
            logger.debug(f"Executing VNC command: {' '.join(full_cmd)}")
            
            # Execute command with timeout
            process = await asyncio.create_subprocess_exec(
                *full_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                if process.returncode == 0:
                    output = stdout.decode().strip() or "Command executed successfully"
                    return SmolToolResult(output=output, success=True)
                else:
                    error = stderr.decode().strip() or "Command failed"
                    return SmolToolResult(error=f"VNC command failed: {error}", success=False)
                    
            except asyncio.TimeoutError:
                try:
                    process.kill()
                    await process.wait()
                except:
                    pass
                return SmolToolResult(
                    error=f"VNC command timed out after {timeout} seconds",
                    success=False
                )
                
        except Exception as e:
            logger.error(f"VNC command execution error: {str(e)}")
            return SmolToolResult(
                error=f"VNC command execution error: {str(e)}",
                success=False
            )
    
    async def _connect(self, host: str, port: int = 5900, password: str = None, timeout: float = 15) -> SmolToolResult:
        """Connect to a VNC server by testing connection"""
        try:
            # Build connection string
            connection_string = self._build_connection_string(host, port)
            
            # Test connection with a simple capture command
            base_cmd = ["vncdotool", "-s", connection_string]
            if password:
                base_cmd.extend(["-p", password])
            
            test_cmd = base_cmd + ["capture", "/tmp/vnc_connection_test.png"]
            logger.debug(f"Testing VNC connection: {' '.join(test_cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *test_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                if process.returncode == 0:
                    # Connection successful, store connection details
                    self._connected_host = host
                    self._connection_string = connection_string
                    self._password = password
                    
                    return SmolToolResult(
                        output=f"Successfully connected to VNC server at {connection_string}",
                        success=True
                    )
                else:
                    error = stderr.decode().strip() or "Connection failed"
                    return SmolToolResult(
                        error=f"Failed to connect to VNC server: {error}",
                        success=False
                    )
                    
            except asyncio.TimeoutError:
                try:
                    process.kill()
                    await process.wait()
                except:
                    pass
                return SmolToolResult(
                    error=f"Connection to VNC server timed out after {timeout} seconds",
                    success=False
                )
                
        except Exception as e:
            logger.error(f"VNC connection error: {str(e)}")
            return SmolToolResult(
                error=f"Failed to connect to VNC server: {str(e)}",
                success=False
            )
    
    async def _disconnect(self, timeout: float = 15) -> SmolToolResult:
        """Disconnect from VNC server"""
        try:
            # Clear connection state
            self._connected_host = None
            self._connection_string = None
            self._password = None
            
            # Also remove the state file
            try:
                if os.path.exists(VNC_STATE_FILE):
                    os.remove(VNC_STATE_FILE)
            except Exception:
                pass
            
            return SmolToolResult(
                output="Successfully disconnected from VNC server",
                success=True
            )
        except Exception as e:
            logger.error(f"Error during disconnection: {str(e)}")
            return SmolToolResult(
                error=f"Error during disconnection: {str(e)}",
                success=False
            )
    
    async def _mouse_move(self, x: int, y: int, timeout: float = 15) -> SmolToolResult:
        """Move mouse to coordinates"""
        result = await self._execute_vnc_command(["mousemove", str(x), str(y)], timeout)
        if result.success:
            result.output = f"Mouse moved to ({x}, {y})"
        return result
    
    async def _mouse_click(self, x: int, y: int, button: int = 1, timeout: float = 15) -> SmolToolResult:
        """Click mouse at coordinates"""
        # Move mouse first
        move_result = await self._execute_vnc_command(["mousemove", str(x), str(y)], timeout)
        if not move_result.success:
            return move_result
        
        # Then click
        click_result = await self._execute_vnc_command(["click", str(button)], timeout)
        if click_result.success:
            click_result.output = f"Mouse clicked at ({x}, {y}) with button {button}"
        return click_result
    
    async def _key_press(self, key: str, timeout: float = 15) -> SmolToolResult:
        """Press a key"""
        result = await self._execute_vnc_command(["key", key], timeout)
        if result.success:
            result.output = f"Key '{key}' pressed"
        return result
    
    async def _type_text(self, text: str, timeout: float = 15) -> SmolToolResult:
        """Type text"""
        result = await self._execute_vnc_command(["type", text], timeout)
        if result.success:
            result.output = f"Typed text: {text}"
        return result
    
    async def _capture_screen(self, filename: str, timeout: float = 15,
                            img_title: str = "VNC Screenshot",
                            img_alt: str = "VNC screen capture",
                            display: str = "true",
                            include_in_next_call: str = "true") -> SmolToolResult:
        """Capture entire screen"""
        result = await self._execute_vnc_command(["capture", filename], timeout)
        if result.success:
            try:
                # Read the captured image and encode it to base64
                with open(filename, 'rb') as img_file:
                    img_data = img_file.read()
                    base64_data = base64.b64encode(img_data).decode('utf-8')
                
                # Create the image tag with base64 data
                img_tag = f'<img title="{img_title}" alt="{img_alt}" src="data:image/png;base64,{base64_data}" display="{display}" include_in_next_call="{include_in_next_call}">'
                
                # Return both the success message and the image tag
                result.output = f"Screen captured and saved to {filename}\n{img_tag}"
            except Exception as e:
                logger.error(f"Error encoding image to base64: {str(e)}")
                result.output = f"Screen captured and saved to {filename} (base64 encoding failed: {str(e)})"
        return result
    
    async def _capture_region(self, x: int, y: int, width: int, height: int, filename: str, timeout: float = 15,
                            img_title: str = "VNC Region Screenshot",
                            img_alt: str = None,
                            display: str = "true",
                            include_in_next_call: str = "true") -> SmolToolResult:
        """Capture a region of the screen"""
        # vncdotool command-line doesn't have direct region capture, so we'll use capture and note the limitation
        result = await self._execute_vnc_command(["capture", filename], timeout)
        if result.success:
            try:
                # Read the captured image and encode it to base64
                with open(filename, 'rb') as img_file:
                    img_data = img_file.read()
                    base64_data = base64.b64encode(img_data).decode('utf-8')
                
                # Use provided alt text or generate default
                if img_alt is None:
                    img_alt = f"VNC region capture at ({x},{y}) {width}x{height}"
                
                # Create the image tag with base64 data
                img_tag = f'<img title="{img_title}" alt="{img_alt}" src="data:image/png;base64,{base64_data}" display="{display}" include_in_next_call="{include_in_next_call}">'
                
                # Return both the success message and the image tag
                result.output = f"Screen captured to {filename} (Note: vncdotool command-line doesn't support region capture, full screen captured instead)\n{img_tag}"
            except Exception as e:
                logger.error(f"Error encoding image to base64: {str(e)}")
                result.output = f"Screen captured to {filename} (Note: vncdotool command-line doesn't support region capture, full screen captured instead) (base64 encoding failed: {str(e)})"
        return result
    
    async def execute(self, action: str, host: str = None, port: int = 5900, password: str = None,
                     x: int = None, y: int = None, button: int = 1, key: str = None,
                     text: str = None, filename: str = None, width: int = None, height: int = None,
                     timeout: float = 15, img_title: str = None, img_alt: str = None,
                     display: str = "true", include_in_next_call: str = "true", **kwargs) -> SmolToolResult:
        """
        Execute VNC automation action using reliable command-line vncdotool.
        
        Args:
            action (str): Action to perform
            host (str): VNC server host
            port (int): VNC server port
            password (str): VNC server password
            x (int): X coordinate for mouse actions
            y (int): Y coordinate for mouse actions
            button (int): Mouse button (1=left, 2=middle, 3=right)
            key (str): Key to press
            text (str): Text to type
            filename (str): Filename for screen capture
            width (int): Width for region capture (not supported in command-line mode)
            height (int): Height for region capture (not supported in command-line mode)
            timeout (float): Timeout for the VNC operation in seconds (default: 15)
            
        Returns:
            SmolToolResult: Result of the VNC operation
        """
        try:
            logger.debug(f"VNC action: {action} with timeout: {timeout}")
            
            if action == "connect":
                if not host:
                    return SmolToolResult(
                        error="host is required for connect action",
                        success=False
                    )
                return await self._connect(host, port, password, timeout)
            
            elif action == "disconnect":
                return await self._disconnect(timeout)
            
            elif action == "mouse_move":
                if x is None or y is None:
                    return SmolToolResult(
                        error="x and y coordinates are required for mouse_move action",
                        success=False
                    )
                return await self._mouse_move(x, y, timeout)
            
            elif action == "mouse_click":
                if x is None or y is None:
                    return SmolToolResult(
                        error="x and y coordinates are required for mouse_click action",
                        success=False
                    )
                return await self._mouse_click(x, y, button, timeout)
            
            elif action == "key_press":
                if not key:
                    return SmolToolResult(
                        error="key is required for key_press action",
                        success=False
                    )
                return await self._key_press(key, timeout)
            
            elif action == "type_text":
                if not text:
                    return SmolToolResult(
                        error="text is required for type_text action",
                        success=False
                    )
                return await self._type_text(text, timeout)
            
            elif action == "capture_screen":
                if not filename:
                    return SmolToolResult(
                        error="filename is required for capture_screen action",
                        success=False
                    )
                # Use provided title/alt or defaults
                title = img_title or "VNC Screenshot"
                alt = img_alt or "VNC screen capture"
                return await self._capture_screen(filename, timeout, title, alt, display, include_in_next_call)
            
            elif action == "capture_region":
                if x is None or y is None or width is None or height is None or not filename:
                    return SmolToolResult(
                        error="x, y, width, height, and filename are required for capture_region action",
                        success=False
                    )
                # Use provided title or default
                title = img_title or "VNC Region Screenshot"
                return await self._capture_region(x, y, width, height, filename, timeout, title, img_alt, display, include_in_next_call)
            
            else:
                return SmolToolResult(
                    error=f"Unknown action: {action}. Available actions: connect, disconnect, mouse_move, mouse_click, key_press, type_text, capture_screen, capture_region",
                    success=False
                )
                
        except Exception as e:
            logger.error(f"VNC tool error: {str(e)}")
            return SmolToolResult(
                error=f"VNC tool error: {str(e)}",
                success=False
            )
    
    async def __aenter__(self):
        """Async context manager entry"""
        logger.debug("=== VNC tool __aenter__() called ===")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        logger.debug(f"=== VNC tool __aexit__() called with exc_type={exc_type}, exc_val={exc_val} ===")
        await self._disconnect()


class SimpleVNCComputerUseTool(AsyncSmolTool):
    """Simplified VNC tool for basic operations using command-line vncdotool"""
    
    def __init__(self):
        self.name = "simple_vnc_computer"
        self.description = """A simplified VNC automation tool using reliable command-line vncdotool for basic operations."""
        
        self.inputs = {
            "action": {
                "type": "string",
                "description": "Action to perform: connect, disconnect, mouse_click, key_press, type_text",
                "required": True
            },
            "host": {
                "type": "string",
                "description": "VNC server host (required for 'connect' action)",
                "required": False
            },
            "port": {
                "type": "integer",
                "description": "VNC server port (default: 5900)",
                "default": 5900,
                "required": False
            },
            "password": {
                "type": "string",
                "description": "VNC server password (optional)",
                "required": False
            },
            "x": {
                "type": "integer",
                "description": "X coordinate for mouse actions",
                "required": False
            },
            "y": {
                "type": "integer",
                "description": "Y coordinate for mouse actions",
                "required": False
            },
            "key": {
                "type": "string",
                "description": "Key to press (required for 'key_press' action)",
                "required": False
            },
            "text": {
                "type": "string",
                "description": "Text to type (required for 'type_text' action)",
                "required": False
            },
            "timeout": {
                "type": "number",
                "description": "Timeout for the VNC operation in seconds (default: 10)",
                "default": 10,
                "required": False
            }
        }
        self.output_type = "string"
        super().__init__()
    
    async def execute(self, action: str, host: str = None, port: int = 5900, password: str = None,
                     x: int = None, y: int = None, key: str = None, text: str = None,
                     timeout: float = 10, **kwargs) -> SmolToolResult:
        """
        Execute simplified VNC automation action using command-line vncdotool.
        
        Args:
            action (str): Action to perform
            host (str): VNC server host
            port (int): VNC server port
            password (str): VNC server password
            x (int): X coordinate for mouse actions
            y (int): Y coordinate for mouse actions
            key (str): Key to press
            text (str): Text to type
            timeout (float): Timeout for the VNC operation in seconds (default: 10)
            
        Returns:
            SmolToolResult: Result of the VNC operation
        """
        try:
            # Use the full VNC tool for actual operations
            full_tool = VNCComputerUseTool()
            
            if action == "connect":
                return await full_tool._connect(host, port, password, timeout)
            elif action == "disconnect":
                return await full_tool._disconnect(timeout)
            elif action == "mouse_click":
                if x is None or y is None:
                    return SmolToolResult(
                        error="x and y coordinates are required for mouse_click action",
                        success=False
                    )
                # Set connection details for the operation
                full_tool._connection_string = full_tool._build_connection_string(host or "localhost", port)
                full_tool._password = password
                return await full_tool._mouse_click(x, y, 1, timeout)
            elif action == "key_press":
                if not key:
                    return SmolToolResult(
                        error="key is required for key_press action",
                        success=False
                    )
                # Set connection details for the operation
                full_tool._connection_string = full_tool._build_connection_string(host or "localhost", port)
                full_tool._password = password
                return await full_tool._key_press(key, timeout)
            elif action == "type_text":
                if not text:
                    return SmolToolResult(
                        error="text is required for type_text action",
                        success=False
                    )
                # Set connection details for the operation
                full_tool._connection_string = full_tool._build_connection_string(host or "localhost", port)
                full_tool._password = password
                return await full_tool._type_text(text, timeout)
            else:
                return SmolToolResult(
                    error=f"Unknown action: {action}. Available actions: connect, disconnect, mouse_click, key_press, type_text",
                    success=False
                )
                
        except Exception as e:
            logger.error(f"Simple VNC tool error: {str(e)}")
            return SmolToolResult(
                error=f"Simple VNC tool error: {str(e)}",
                success=False
            )