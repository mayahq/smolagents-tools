"""
Python code execution tool adapted for smolagents
"""

import multiprocessing
import sys
from io import StringIO
from typing import Dict
from .base import AsyncSmolTool, SmolToolResult


class PythonExecutorTool(AsyncSmolTool):
    """
    A tool for executing Python code with timeout and safety restrictions
    Adapted from OpenManus PythonExecute
    """
    
    def __init__(self):
        self.name = "python_executor"
        self.description = """Executes Python code string. Note: Only print outputs are visible, function return values are not captured. Use print statements to see results."""
        
        self.inputs = {
            "code": {
                "type": "string",
                "description": "The Python code to execute.",
                "required": True
            },
            "timeout": {
                "type": "integer",
                "description": "Execution timeout in seconds. Default is 30.",
                "default": 30,
                "required": False
            }
        }
        self.output_type = "string"
        super().__init__()
    
    def _run_code(self, code: str, result_dict: dict, safe_globals: dict) -> None:
        """Run code in a separate process"""
        original_stdout = sys.stdout
        try:
            output_buffer = StringIO()
            sys.stdout = output_buffer
            exec(code, safe_globals, safe_globals)
            result_dict["output"] = output_buffer.getvalue()
            result_dict["success"] = True
        except Exception as e:
            result_dict["output"] = str(e)
            result_dict["success"] = False
        finally:
            sys.stdout = original_stdout
    
    async def execute(self, code: str, timeout: int = 30, **kwargs) -> SmolToolResult:
        """
        Executes the provided Python code with a timeout.
        
        Args:
            code (str): The Python code to execute.
            timeout (int): Execution timeout in seconds.
            
        Returns:
            SmolToolResult: Contains execution output or error message and success status.
        """
        try:
            with multiprocessing.Manager() as manager:
                result = manager.dict({"output": "", "success": False})
                
                # Create safe globals for execution
                if isinstance(__builtins__, dict):
                    safe_globals = {"__builtins__": __builtins__}
                else:
                    safe_globals = {"__builtins__": __builtins__.__dict__.copy()}
                
                # Start process
                proc = multiprocessing.Process(
                    target=self._run_code, 
                    args=(code, result, safe_globals)
                )
                proc.start()
                proc.join(timeout)
                
                # Check for timeout
                if proc.is_alive():
                    proc.terminate()
                    proc.join(1)
                    return SmolToolResult(
                        output=f"Execution timeout after {timeout} seconds",
                        error=f"Code execution timed out after {timeout} seconds",
                        success=False
                    )
                
                # Return results
                result_dict = dict(result)
                if result_dict["success"]:
                    return SmolToolResult(
                        output=result_dict["output"] or "Code executed successfully (no output)",
                        success=True
                    )
                else:
                    return SmolToolResult(
                        output="",
                        error=result_dict["output"],
                        success=False
                    )
                    
        except Exception as e:
            return SmolToolResult(
                error=f"Python execution failed: {str(e)}",
                success=False
            )


class SafePythonExecutorTool(PythonExecutorTool):
    """
    A safer version of Python executor with restricted imports and operations
    """
    
    def __init__(self):
        super().__init__()
        self.name = "safe_python_executor"
        self.description = """Executes Python code with safety restrictions. Certain dangerous operations and imports are blocked."""
        
        # Define restricted modules and functions
        self.restricted_modules = {
            'os', 'sys', 'subprocess', 'shutil', 'glob', 'pickle', 'marshal',
            'importlib', '__import__', 'eval', 'exec', 'compile', 'open'
        }
        
        self.restricted_functions = {
            'eval', 'exec', 'compile', '__import__', 'open', 'input', 'raw_input'
        }
        
        # Re-initialize with updated name
        super().__init__()
    
    def _create_safe_globals(self):
        """Create a restricted global environment"""
        safe_builtins = {}
        
        # Copy safe builtins
        if isinstance(__builtins__, dict):
            original_builtins = __builtins__
        else:
            original_builtins = __builtins__.__dict__
        
        for name, value in original_builtins.items():
            if name not in self.restricted_functions:
                safe_builtins[name] = value
        
        # Add safe print function
        safe_builtins['print'] = print
        
        return {"__builtins__": safe_builtins}
    
    def _run_code(self, code: str, result_dict: dict, safe_globals: dict) -> None:
        """Run code with safety checks"""
        original_stdout = sys.stdout
        try:
            # Check for restricted imports in code
            for module in self.restricted_modules:
                if f"import {module}" in code or f"from {module}" in code:
                    result_dict["output"] = f"Restricted module '{module}' is not allowed"
                    result_dict["success"] = False
                    return
            
            # Check for restricted functions
            for func in self.restricted_functions:
                if func in code:
                    result_dict["output"] = f"Restricted function '{func}' is not allowed"
                    result_dict["success"] = False
                    return
            
            output_buffer = StringIO()
            sys.stdout = output_buffer
            
            # Use the safe globals
            exec(code, safe_globals, safe_globals)
            
            result_dict["output"] = output_buffer.getvalue()
            result_dict["success"] = True
            
        except Exception as e:
            result_dict["output"] = str(e)
            result_dict["success"] = False
        finally:
            sys.stdout = original_stdout
    
    async def execute(self, code: str, timeout: int = 30, **kwargs) -> SmolToolResult:
        """Execute code with safety restrictions"""
        try:
            with multiprocessing.Manager() as manager:
                result = manager.dict({"output": "", "success": False})
                safe_globals = self._create_safe_globals()
                
                proc = multiprocessing.Process(
                    target=self._run_code,
                    args=(code, result, safe_globals)
                )
                proc.start()
                proc.join(timeout)
                
                if proc.is_alive():
                    proc.terminate()
                    proc.join(1)
                    return SmolToolResult(
                        output=f"Execution timeout after {timeout} seconds",
                        error=f"Code execution timed out after {timeout} seconds",
                        success=False
                    )
                
                result_dict = dict(result)
                if result_dict["success"]:
                    return SmolToolResult(
                        output=result_dict["output"] or "Code executed successfully (no output)",
                        success=True
                    )
                else:
                    return SmolToolResult(
                        output="",
                        error=result_dict["output"],
                        success=False
                    )
                    
        except Exception as e:
            return SmolToolResult(
                error=f"Safe Python execution failed: {str(e)}",
                success=False
            )