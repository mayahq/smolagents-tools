"""
Base classes for smolagents tools adapted from OpenManus
"""

import asyncio
import concurrent.futures
from typing import Any, Dict, Optional, Union
from smolagents import Tool


class SmolToolResult:
    """
    Result object for smolagents tools, adapted from OpenManus ToolResult
    """
    
    def __init__(self, output: str = "", error: str = "", success: bool = True, 
                 artifacts: Optional[Dict[str, Any]] = None, base64_image: str = "", 
                 system: str = ""):
        self.output = output
        self.error = error
        self.success = success
        self.artifacts = artifacts or {}
        self.base64_image = base64_image
        self.system = system
    
    def __str__(self):
        if self.success:
            return self.output
        else:
            return f"Error: {self.error}"
    
    def __repr__(self):
        return f"SmolToolResult(success={self.success}, output='{self.output[:50]}...', error='{self.error}')"
    
    def to_dict(self):
        """Convert to dictionary for serialization"""
        result = {
            "output": self.output,
            "error": self.error,
            "success": self.success,
            "artifacts": self.artifacts
        }
        if self.base64_image:
            result["base64_image"] = self.base64_image
        if self.system:
            result["system"] = self.system
        return result


class SmolTool(Tool):
    """
    Base class for smolagents tools adapted from OpenManus BaseTool
    
    This class bridges the gap between OpenManus async tools and smolagents sync tools
    """
    
    def __init__(self):
        # Set default attributes that smolagents expects if not already set by child class
        if not hasattr(self, 'name') or not getattr(self, 'name', None):
            self.name = self.__class__.__name__.lower().replace('tool', '')
        if not hasattr(self, 'description') or not getattr(self, 'description', None):
            self.description = f"Tool for {self.name}"
        if not hasattr(self, 'inputs') or not getattr(self, 'inputs', None):
            self.inputs = {}
        if not hasattr(self, 'output_type') or not getattr(self, 'output_type', None):
            self.output_type = "string"
        
        # Call parent init after setting attributes
        super().__init__()
        
        # Fix inputs to be smolagents compatible
        self._fix_inputs_for_smolagents()
        
        # Create the forward method dynamically based on inputs
        self._create_forward_method()
    
    def _fix_inputs_for_smolagents(self):
        """Fix input definitions to be compatible with smolagents requirements"""
        for input_name, input_def in self.inputs.items():
            # If input is not required, it must be nullable
            if not input_def.get('required', False):
                input_def['nullable'] = True
    
    def _create_forward_method(self):
        """Create forward method with proper signature based on inputs"""
        input_names = list(self.inputs.keys())
        
        # Create parameter list for the method signature
        params = ['self']
        defaults = []
        
        for input_name in input_names:
            input_def = self.inputs[input_name]
            if input_def.get('required', False):
                params.append(input_name)
            else:
                params.append(input_name)
                # Add default value
                default_val = input_def.get('default', None)
                defaults.append(default_val)
        
        # Create the method signature string
        if defaults:
            # Calculate how many params have defaults
            num_defaults = len(defaults)
            required_params = params[1:-num_defaults]  # Skip 'self' and params with defaults
            default_params = params[-num_defaults:]
            
            sig_parts = required_params + [f"{p}=None" for p in default_params]
        else:
            sig_parts = params[1:]  # Skip 'self'
        
        signature = ', '.join(sig_parts)
        
        # Create kwargs assignment lines
        kwargs_lines = []
        for name in input_names:
            kwargs_lines.append(f"    kwargs['{name}'] = {name}")
        kwargs_code = '\n'.join(kwargs_lines)
        
        # Create the method code
        method_code = f"""def forward(self, {signature}):
    '''Forward method with proper signature for smolagents'''
    kwargs = {{}}
{kwargs_code}
    return self._execute_with_kwargs(**kwargs)
"""
        
        # Execute the method code to create the method
        namespace = {}
        exec(method_code, namespace)
        
        # Bind the method to the instance
        import types
        self.forward = types.MethodType(namespace['forward'], self)
    
    def _execute_with_kwargs(self, **kwargs):
        """
        Internal method to execute with kwargs - synchronous wrapper around async execute
        """
        try:
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an event loop, use thread pool to run async code
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self._run_async_in_thread, **kwargs)
                    result = future.result()
                    if isinstance(result, SmolToolResult):
                        return result.output if result.success else f"Error: {result.error}"
                    else:
                        return str(result)
            except RuntimeError:
                # No event loop running, create a new one
                result = asyncio.run(self.execute(**kwargs))
                if isinstance(result, SmolToolResult):
                    return result.output if result.success else f"Error: {result.error}"
                else:
                    return str(result)
        except Exception as e:
            return f"Error executing tool: {str(e)}"
    
    def _run_async_in_thread(self, **kwargs):
        """Run async execute in a new thread with its own event loop"""
        return asyncio.run(self.execute(**kwargs))
    
    async def execute(self, **kwargs) -> SmolToolResult:
        """
        Execute the tool with given parameters.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement execute method")


class AsyncSmolTool(SmolTool):
    """
    Async version of SmolTool for tools that need async execution
    """
    
    def __init__(self):
        super().__init__()
    
    async def execute(self, **kwargs) -> SmolToolResult:
        """
        Execute the tool asynchronously.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement execute method")


def sync_to_async(func):
    """Decorator to convert sync function to async"""
    async def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def async_to_sync(async_func):
    """Convert async function to sync by running in event loop"""
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an event loop, we need to use a different approach
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, async_func(*args, **kwargs))
                    return future.result()
            else:
                return loop.run_until_complete(async_func(*args, **kwargs))
        except RuntimeError:
            # No event loop running, create a new one
            return asyncio.run(async_func(*args, **kwargs))
    return wrapper