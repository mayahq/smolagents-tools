"""
File editing tool adapted for smolagents
"""

import os
from pathlib import Path
from typing import List, Optional, Literal
from collections import defaultdict
from .base import AsyncSmolTool, SmolToolResult


class FileEditorTool(AsyncSmolTool):
    """
    A tool for editing files with various operations like create, read, write, and str_replace
    Adapted from OpenManus StrReplaceEditor
    """
    
    def __init__(self):
        self.name = "file_editor"
        self.description = """A tool for viewing and editing files. Can create, read, write files and perform string replacements."""
        
        self.inputs = {
            "command": {
                "type": "string",
                "description": "The command to execute. One of: view, create, str_replace, undo_edit",
                "required": True
            },
            "path": {
                "type": "string", 
                "description": "Absolute path to file",
                "required": True
            },
            "file_text": {
                "type": "string",
                "description": "Required for 'create' command. Text content to write to file.",
                "required": False
            },
            "old_str": {
                "type": "string",
                "description": "Required for 'str_replace' command. String to be replaced.",
                "required": False
            },
            "new_str": {
                "type": "string", 
                "description": "Required for 'str_replace' command. String to replace with.",
                "required": False
            },
            "view_range": {
                "type": "string",
                "description": "Optional for 'view' command. Range of lines to view, e.g., '[1, 50]'",
                "required": False
            }
        }
        self.output_type = "string"
        
        # Track file states for undo functionality
        self._file_states = defaultdict(list)
        super().__init__()
    
    def _save_file_state(self, path: str) -> None:
        """Save current file state for undo"""
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self._file_states[path].append(content)
                # Keep only last 10 states
                if len(self._file_states[path]) > 10:
                    self._file_states[path].pop(0)
        except Exception:
            pass
    
    def _view_file(self, path: str, view_range: Optional[str] = None) -> SmolToolResult:
        """View file contents"""
        try:
            if not os.path.exists(path):
                return SmolToolResult(
                    error=f"File not found: {path}",
                    success=False
                )
            
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if view_range:
                try:
                    # Parse range like [1, 50]
                    range_str = view_range.strip('[]')
                    start, end = map(int, range_str.split(','))
                    start = max(1, start) - 1  # Convert to 0-based
                    end = min(len(lines), end)
                    lines = lines[start:end]
                    
                    output = f"Here's the result of running `view` on {path} (lines {start+1}-{end}):\n"
                except Exception:
                    output = f"Here's the result of running `view` on {path}:\n"
            else:
                output = f"Here's the result of running `view` on {path}:\n"
            
            # Add line numbers
            for i, line in enumerate(lines, 1):
                output += f"{i:6}|{line}"
            
            return SmolToolResult(output=output, success=True)
            
        except Exception as e:
            return SmolToolResult(
                error=f"Error viewing file: {str(e)}",
                success=False
            )
    
    def _create_file(self, path: str, file_text: str) -> SmolToolResult:
        """Create a new file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Check if file already exists
            if os.path.exists(path):
                return SmolToolResult(
                    error=f"File already exists: {path}. Use str_replace to edit.",
                    success=False
                )
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(file_text)
            
            return SmolToolResult(
                output=f"File created successfully at {path}",
                success=True
            )
            
        except Exception as e:
            return SmolToolResult(
                error=f"Error creating file: {str(e)}",
                success=False
            )
    
    def _str_replace(self, path: str, old_str: str, new_str: str) -> SmolToolResult:
        """Replace string in file"""
        try:
            if not os.path.exists(path):
                return SmolToolResult(
                    error=f"File not found: {path}",
                    success=False
                )
            
            # Save current state for undo
            self._save_file_state(path)
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if old_str not in content:
                return SmolToolResult(
                    error=f"String not found in file: {old_str}",
                    success=False
                )
            
            # Count occurrences
            count = content.count(old_str)
            if count > 1:
                return SmolToolResult(
                    error=f"Multiple occurrences found ({count}). Please be more specific.",
                    success=False
                )
            
            # Replace string
            new_content = content.replace(old_str, new_str)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return SmolToolResult(
                output=f"String replaced successfully in {path}",
                success=True
            )
            
        except Exception as e:
            return SmolToolResult(
                error=f"Error replacing string: {str(e)}",
                success=False
            )
    
    def _undo_edit(self, path: str) -> SmolToolResult:
        """Undo last edit"""
        try:
            if path not in self._file_states or not self._file_states[path]:
                return SmolToolResult(
                    error=f"No previous state found for {path}",
                    success=False
                )
            
            # Restore previous state
            previous_content = self._file_states[path].pop()
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(previous_content)
            
            return SmolToolResult(
                output=f"Undid last edit to {path}",
                success=True
            )
            
        except Exception as e:
            return SmolToolResult(
                error=f"Error undoing edit: {str(e)}",
                success=False
            )
    
    async def execute(self, command: str, path: str, file_text: str = None,
                     old_str: str = None, new_str: str = None,
                     view_range: str = None, timeout: int = 30, **kwargs) -> SmolToolResult:
        """
        Execute file editing command.
        
        Args:
            command (str): Command to execute (view, create, str_replace, undo_edit)
            path (str): File path
            file_text (str): Content for create command
            old_str (str): String to replace for str_replace command
            new_str (str): Replacement string for str_replace command
            view_range (str): Line range for view command
            timeout (int): Timeout in seconds for file operations
            
        Returns:
            SmolToolResult: Result of the operation
        """
        try:
            # Convert to absolute path
            path = os.path.abspath(path)
            
            if command == "view":
                return self._view_file(path, view_range)
            
            elif command == "create":
                if file_text is None:
                    return SmolToolResult(
                        error="file_text is required for create command",
                        success=False
                    )
                return self._create_file(path, file_text)
            
            elif command == "str_replace":
                if old_str is None or new_str is None:
                    return SmolToolResult(
                        error="old_str and new_str are required for str_replace command",
                        success=False
                    )
                return self._str_replace(path, old_str, new_str)
            
            elif command == "undo_edit":
                return self._undo_edit(path)
            
            else:
                return SmolToolResult(
                    error=f"Unknown command: {command}. Use view, create, str_replace, or undo_edit",
                    success=False
                )
                
        except Exception as e:
            return SmolToolResult(
                error=f"File editor error: {str(e)}",
                success=False
            )


class SimpleFileReaderTool(AsyncSmolTool):
    """Simple tool for reading file contents"""
    
    def __init__(self):
        self.name = "file_reader"
        self.description = "Read the contents of a file"
        
        self.inputs = {
            "path": {
                "type": "string",
                "description": "Path to the file to read",
                "required": True
            }
        }
        self.output_type = "string"
        super().__init__()
    
    async def execute(self, path: str, timeout: int = 30, **kwargs) -> SmolToolResult:
        """Read file contents"""
        try:
            if not os.path.exists(path):
                return SmolToolResult(
                    error=f"File not found: {path}",
                    success=False
                )
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return SmolToolResult(
                output=content,
                success=True
            )
            
        except Exception as e:
            return SmolToolResult(
                error=f"Error reading file: {str(e)}",
                success=False
            )


class SimpleFileWriterTool(AsyncSmolTool):
    """Simple tool for writing file contents"""
    
    def __init__(self):
        self.name = "file_writer"
        self.description = "Write content to a file"
        
        self.inputs = {
            "path": {
                "type": "string",
                "description": "Path to the file to write",
                "required": True
            },
            "content": {
                "type": "string",
                "description": "Content to write to the file",
                "required": True
            }
        }
        self.output_type = "string"
        super().__init__()
    
    async def execute(self, path: str, content: str, timeout: int = 30, **kwargs) -> SmolToolResult:
        """Write content to file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return SmolToolResult(
                output=f"Successfully wrote to {path}",
                success=True
            )
            
        except Exception as e:
            return SmolToolResult(
                error=f"Error writing file: {str(e)}",
                success=False
            )