"""
Bash command execution tool adapted for smolagents
"""

import asyncio
import os
from typing import Optional
from .base import AsyncSmolTool, SmolToolResult


class BashSession:
    """A session of a bash shell, adapted from OpenManus"""
    
    def __init__(self, timeout: float = 120.0):
        self._started = False
        self._process = None
        self._timed_out = False
        self.command = "/bin/bash"
        self._output_delay = 0.2  # seconds
        self._timeout = timeout  # seconds
        self._sentinel = "<<exit>>"
    
    async def start(self):
        if self._started:
            return
        
        self._process = await asyncio.create_subprocess_shell(
            self.command,
            preexec_fn=os.setsid,
            shell=True,
            bufsize=0,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        self._started = True
    
    def stop(self):
        """Terminate the bash shell."""
        if not self._started or not self._process:
            return
        if self._process.returncode is not None:
            return
        self._process.terminate()
    
    async def run(self, command: str):
        """Execute a command in the bash shell."""
        if not self._started:
            raise Exception("Session has not started.")
        if self._process.returncode is not None:
            return SmolToolResult(
                system="tool must be restarted",
                error=f"bash has exited with returncode {self._process.returncode}",
                success=False
            )
        if self._timed_out:
            raise Exception(
                f"timed out: bash has not returned in {self._timeout} seconds and must be restarted"
            )
        
        # Send command to the process
        self._process.stdin.write(
            command.encode() + f"; echo '{self._sentinel}'\n".encode()
        )
        await self._process.stdin.drain()
        
        # Read output from the process, until the sentinel is found
        try:
            async def read_until_sentinel():
                while True:
                    await asyncio.sleep(self._output_delay)
                    output = self._process.stdout._buffer.decode()
                    if self._sentinel in output:
                        return output[:output.index(self._sentinel)]
            
            output = await asyncio.wait_for(read_until_sentinel(), timeout=self._timeout)
        except asyncio.TimeoutError:
            self._timed_out = True
            # Capture any output that was available before timeout
            output = self._process.stdout._buffer.decode()
            error = self._process.stderr._buffer.decode()
            
            # Clean up output
            if output.endswith("\n"):
                output = output[:-1]
            if error.endswith("\n"):
                error = error[:-1]
            
            # Clear the buffers
            self._process.stdout._buffer.clear()
            self._process.stderr._buffer.clear()
            
            # Return partial results with timeout error
            timeout_msg = f"Command timed out after {self._timeout} seconds"
            if error:
                error = f"{timeout_msg}\nOriginal stderr: {error}"
            else:
                error = timeout_msg
            
            return SmolToolResult(
                output=output if output else "",
                error=error,
                success=False
            )
        
        if output.endswith("\n"):
            output = output[:-1]
        
        error = self._process.stderr._buffer.decode()
        if error.endswith("\n"):
            error = error[:-1]
        
        # Clear the buffers
        self._process.stdout._buffer.clear()
        self._process.stderr._buffer.clear()
        
        return SmolToolResult(output=output, error=error if error else None)


class BashTool(AsyncSmolTool):
    """
    Execute bash commands in the terminal, adapted from OpenManus Bash tool
    """
    
    def __init__(self):
        self.name = "bash"
        self.description = """Execute a bash command in the terminal.
* Long running commands: For commands that may run indefinitely, it should be run in the background and the output should be redirected to a file, e.g. command = `python3 app.py > server.log 2>&1 &`.
* Interactive: If a bash command returns exit code `-1`, this means the process is not yet finished. The assistant must then send a second call to terminal with an empty `command` (which will retrieve any additional logs), or it can send additional text (set `command` to the text) to STDIN of the running process, or it can send command=`ctrl+c` to interrupt the process.
* Timeout: If a command execution result says "Command timed out. Sending SIGINT to the process", the assistant should retry running the command in the background."""
        
        self.inputs = {
            "command": {
                "type": "string",
                "description": "The bash command to execute. Can be empty to view additional logs when previous exit code is `-1`. Can be `ctrl+c` to interrupt the currently running process.",
                "required": True
            }
        }
        self.output_type = "string"
        self._session: Optional[BashSession] = None
        super().__init__()
    
    async def execute(self, command: str = None, restart: bool = False, timeout: int = 120, **kwargs) -> SmolToolResult:
        """Execute a bash command"""
        try:
            if restart:
                if self._session:
                    self._session.stop()
                self._session = BashSession(timeout=float(timeout))
                await self._session.start()
                return SmolToolResult(system="tool has been restarted.", output="Bash session restarted")
            
            if self._session is None:
                self._session = BashSession(timeout=float(timeout))
                await self._session.start()
            else:
                # Update timeout for existing session
                self._session._timeout = float(timeout)
            
            if command is not None:
                result = await self._session.run(command)
                return result
            
            return SmolToolResult(error="no command provided.", success=False)
            
        except Exception as e:
            return SmolToolResult(error=f"Bash execution failed: {str(e)}", success=False)
    
    def __del__(self):
        """Cleanup when tool is destroyed"""
        if self._session:
            self._session.stop()