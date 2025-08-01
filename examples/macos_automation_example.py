"""
Example usage of the macOS automation tool

This example demonstrates how to use the macOS automation tool to:
1. Open applications
2. Interact with UI elements
3. Execute AppleScript
4. Take screenshots

Prerequisites:
- macOS system
- mlx-use library installed: pip install mlx-use
- Accessibility permissions enabled for the terminal/IDE
"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import smolagents_tools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from smolagents_tools import create_tool


async def basic_macos_example():
    """Basic example using SimpleMacOSTool"""
    print("🍎 Basic macOS Automation Example")
    print("=" * 40)
    
    # Create the simple macOS tool
    macos_tool = create_tool("simple_macos")
    if not macos_tool:
        print("❌ Failed to create macOS tool. Make sure mlx-use is installed.")
        return
    
    print("✅ Created SimpleMacOSTool")
    
    # Example 1: Text-to-speech
    print("\n📢 Example 1: Text-to-speech")
    result = await macos_tool.execute(
        action="say_text",
        text="Hello! This is macOS automation in action!"
    )
    print(f"Result: {result}")
    
    # Example 2: Open Calculator app
    print("\n🧮 Example 2: Opening Calculator app")
    result = await macos_tool.execute(
        action="open_app",
        app_name="Calculator"
    )
    print(f"Result: {result}")
    
    # Example 3: Execute AppleScript
    print("\n📜 Example 3: Execute AppleScript")
    script = '''
    tell application "Finder"
        get the name of the startup disk
    end tell
    '''
    result = await macos_tool.execute(
        action="run_script",
        script=script
    )
    print(f"Result: {result}")


async def advanced_macos_example():
    """Advanced example using MacOSUseTool"""
    print("\n🍎 Advanced macOS Automation Example")
    print("=" * 40)
    
    # Create the full macOS tool
    macos_tool = create_tool("macos")
    if not macos_tool:
        print("❌ Failed to create macOS tool. Make sure mlx-use is installed.")
        return
    
    print("✅ Created MacOSUseTool")
    
    try:
        # Example 1: Open TextEdit
        print("\n📝 Example 1: Opening TextEdit")
        result = await macos_tool.execute(
            action="open_app",
            app_name="TextEdit"
        )
        print(f"Result: {result}")
        
        if result.success:
            # Wait for app to load
            await asyncio.sleep(2)
            
            # Example 2: Get UI tree
            print("\n🌳 Example 2: Getting UI tree")
            result = await macos_tool.execute(action="get_ui_tree")
            print(f"UI Tree (first 300 chars): {result.output[:300]}...")
            
            # Example 3: Take screenshot
            print("\n📸 Example 3: Taking screenshot")
            result = await macos_tool.execute(action="screenshot")
            print(f"Screenshot result: {result}")
        
        # Example 4: AppleScript to create a new document
        print("\n📜 Example 4: Create new document with AppleScript")
        script = '''
        tell application "TextEdit"
            activate
            make new document
            set text of document 1 to "Hello from macOS automation!\\n\\nThis document was created using the macOS automation tool."
        end tell
        '''
        result = await macos_tool.execute(
            action="run_applescript",
            script=script
        )
        print(f"AppleScript result: {result}")
        
        # Example 5: Get updated UI tree after creating document
        if result.success:
            await asyncio.sleep(1)
            print("\n🌳 Example 5: Getting updated UI tree")
            result = await macos_tool.execute(action="get_ui_tree")
            print(f"Updated UI Tree (first 300 chars): {result.output[:300]}...")
        
    finally:
        # Clean up
        print("\n🧹 Cleaning up...")
        await macos_tool.execute(action="close")


async def calculator_automation_example():
    """Example of automating Calculator app"""
    print("\n🧮 Calculator Automation Example")
    print("=" * 40)
    
    macos_tool = create_tool("macos")
    if not macos_tool:
        print("❌ Failed to create macOS tool")
        return
    
    try:
        # Open Calculator
        print("Opening Calculator...")
        result = await macos_tool.execute(action="open_app", app_name="Calculator")
        if not result.success:
            print(f"Failed to open Calculator: {result}")
            return
        
        await asyncio.sleep(2)  # Wait for app to load
        
        # Get UI tree to see available buttons
        print("Getting Calculator UI tree...")
        result = await macos_tool.execute(action="get_ui_tree")
        print(f"Calculator UI elements:\n{result.output}")
        
        # Note: To actually click buttons, you would need to:
        # 1. Parse the UI tree to find button indices
        # 2. Use click_element action with the appropriate indices
        # 3. This requires the specific UI structure of Calculator
        
        print("\n💡 To perform calculations:")
        print("1. Parse the UI tree output above to find button indices")
        print("2. Use click_element action with those indices")
        print("3. Example: await macos_tool.execute(action='click_element', element_index=5)")
        
    finally:
        await macos_tool.execute(action="close")


async def main():
    """Run all examples"""
    print("🚀 macOS Automation Tool Examples")
    print("=" * 50)
    
    # Check if we're on macOS
    if sys.platform != "darwin":
        print("⚠️  Warning: These examples are designed for macOS systems")
        print(f"Current platform: {sys.platform}")
        return
    
    try:
        # Run basic example
        await basic_macos_example()
        
        # Wait a bit between examples
        await asyncio.sleep(2)
        
        # Run advanced example
        await advanced_macos_example()
        
        # Wait a bit between examples
        await asyncio.sleep(2)
        
        # Run calculator example
        await calculator_automation_example()
        
        print("\n✅ All examples completed!")
        print("\n📝 Notes:")
        print("- Make sure Accessibility permissions are enabled")
        print("- Some actions may require user confirmation")
        print("- UI element indices may vary between app versions")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())