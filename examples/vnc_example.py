"""
Example usage of VNC Computer Use Tool
"""

import asyncio
from smolagents_tools import create_tool


async def main():
    """Example of using the VNC Computer Use Tool"""
    
    # Create the VNC tool
    vnc_tool = create_tool("vnc_computer")
    
    if vnc_tool is None:
        print("VNC tool is not available. Please ensure vncdotool is installed.")
        return
    
    print("VNC Computer Use Tool Example")
    print("=" * 40)
    
    # Example 1: Connect to a VNC server (this would fail without a real VNC server)
    print("Example 1: Connecting to VNC server")
    try:
        result = await vnc_tool.execute(
            action="connect",
            host="localhost",
            port=5900
        )
        print(f"Connection result: {result}")
    except Exception as e:
        print(f"Connection failed (expected without real VNC server): {e}")
    
    # Example 2: Simple VNC tool usage
    print("\nExample 2: Using Simple VNC Computer Use Tool")
    simple_vnc_tool = create_tool("simple_vnc_computer")
    
    if simple_vnc_tool:
        try:
            result = await simple_vnc_tool.execute(
                action="connect",
                host="localhost",
                port=5900
            )
            print(f"Simple VNC connection result: {result}")
        except Exception as e:
            print(f"Simple VNC connection failed (expected without real VNC server): {e}")
    else:
        print("Simple VNC tool is not available.")
    
    print("\nNote: These examples require a real VNC server to run successfully.")
    print("The examples demonstrate the tool structure and interface.")


if __name__ == "__main__":
    asyncio.run(main())