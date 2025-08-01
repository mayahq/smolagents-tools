# macOS Automation Tool

The macOS automation tool provides comprehensive automation capabilities for macOS applications using the `mlx-use` library. It enables AI agents to interact with native macOS applications through the Accessibility API.

## Features

- **App Management**: Open and manage macOS applications
- **UI Interaction**: Click buttons, input text, scroll, and right-click elements
- **AppleScript Execution**: Run custom AppleScript code
- **UI Tree Analysis**: Get detailed information about application UI structure
- **Screenshot Capture**: Take screenshots of the current screen
- **Accessibility Integration**: Full integration with macOS Accessibility API

## Prerequisites

### System Requirements
- macOS 10.14 or later
- Python 3.11+
- Accessibility permissions enabled

### Dependencies
```bash
pip install mlx-use>=0.0.3
pip install pyobjc>=11.0.0
pip install pycocoa>=25.1.18
```

### Accessibility Permissions
1. Go to **System Preferences** → **Security & Privacy** → **Privacy** → **Accessibility**
2. Add your terminal application or IDE to the list
3. Enable the checkbox for your application

## Available Tools

### 1. MacOSUseTool
Full-featured macOS automation tool with comprehensive UI interaction capabilities.

**Actions:**
- `open_app`: Open a macOS application
- `get_ui_tree`: Get the UI element tree of the current application
- `click_element`: Click a UI element by index
- `input_text`: Input text into a UI element
- `right_click`: Right-click a UI element
- `scroll`: Scroll a UI element
- `run_applescript`: Execute AppleScript code
- `screenshot`: Take a screenshot
- `close`: Close the automation session

### 2. SimpleMacOSTool
Simplified tool for basic macOS operations.

**Actions:**
- `open_app`: Open a macOS application
- `run_script`: Execute AppleScript code
- `say_text`: Use text-to-speech

## Usage Examples

### Basic Usage with SimpleMacOSTool

```python
import asyncio
from smolagents_tools import create_tool

async def basic_example():
    # Create the tool
    macos_tool = create_tool("simple_macos")
    
    # Text-to-speech
    result = await macos_tool.execute(
        action="say_text",
        text="Hello from macOS automation!"
    )
    print(result)
    
    # Open an application
    result = await macos_tool.execute(
        action="open_app",
        app_name="Calculator"
    )
    print(result)
    
    # Execute AppleScript
    script = '''
    tell application "Finder"
        get the name of the startup disk
    end tell
    '''
    result = await macos_tool.execute(
        action="run_script",
        script=script
    )
    print(result)

asyncio.run(basic_example())
```

### Advanced Usage with MacOSUseTool

```python
import asyncio
from smolagents_tools import create_tool

async def advanced_example():
    macos_tool = create_tool("macos")
    
    try:
        # Open TextEdit
        result = await macos_tool.execute(
            action="open_app",
            app_name="TextEdit"
        )
        
        if result.success:
            # Wait for app to load
            await asyncio.sleep(2)
            
            # Get UI tree to see available elements
            result = await macos_tool.execute(action="get_ui_tree")
            print("Available UI elements:")
            print(result.output)
            
            # Create a new document with AppleScript
            script = '''
            tell application "TextEdit"
                make new document
                set text of document 1 to "Hello from automation!"
            end tell
            '''
            result = await macos_tool.execute(
                action="run_applescript",
                script=script
            )
            
            # Take a screenshot
            result = await macos_tool.execute(action="screenshot")
            print(f"Screenshot: {result}")
            
    finally:
        # Always clean up
        await macos_tool.execute(action="close")

asyncio.run(advanced_example())
```

### UI Element Interaction

```python
async def ui_interaction_example():
    macos_tool = create_tool("macos")
    
    try:
        # Open Calculator
        await macos_tool.execute(action="open_app", app_name="Calculator")
        await asyncio.sleep(2)
        
        # Get UI tree to find button indices
        result = await macos_tool.execute(action="get_ui_tree")
        print("Calculator UI elements:")
        print(result.output)
        
        # Click elements (indices depend on UI structure)
        # Example: Click number 5 button (index would be from UI tree)
        # await macos_tool.execute(
        #     action="click_element",
        #     element_index=10,  # Example index
        #     click_action="AXPress"
        # )
        
        # Input text into a text field (if available)
        # await macos_tool.execute(
        #     action="input_text",
        #     element_index=5,  # Example index
        #     text="Hello",
        #     submit=False
        # )
        
    finally:
        await macos_tool.execute(action="close")
```

## Tool Parameters

### MacOSUseTool Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `action` | string | Action to perform | Yes |
| `app_name` | string | App name for open_app | No |
| `element_index` | integer | UI element index | No |
| `text` | string | Text for input_text | No |
| `submit` | boolean | Submit after text input | No |
| `click_action` | string | Click action type | No |
| `scroll_direction` | string | Scroll direction | No |
| `script` | string | AppleScript code | No |

### Click Actions
- `AXPress`: Standard button press
- `AXClick`: Standard click
- `AXOpen`: Open action
- `AXConfirm`: Confirm action
- `AXShowMenu`: Show context menu

### Scroll Directions
- `up`: Scroll up
- `down`: Scroll down
- `left`: Scroll left
- `right`: Scroll right

## Common Use Cases

### 1. Application Testing
```python
# Open app and verify UI elements
await macos_tool.execute(action="open_app", app_name="MyApp")
ui_tree = await macos_tool.execute(action="get_ui_tree")
# Verify expected elements are present
```

### 2. Data Entry Automation
```python
# Fill forms automatically
await macos_tool.execute(action="input_text", element_index=1, text="John Doe")
await macos_tool.execute(action="input_text", element_index=2, text="john@example.com")
await macos_tool.execute(action="click_element", element_index=3)  # Submit button
```

### 3. System Administration
```python
# Execute system commands via AppleScript
script = '''
do shell script "system_profiler SPHardwareDataType" with administrator privileges
'''
result = await macos_tool.execute(action="run_applescript", script=script)
```

### 4. Content Creation
```python
# Create and format documents
script = '''
tell application "Pages"
    make new document
    set text of document 1 to "Automated Report\\n\\nGenerated on " & (current date)
end tell
'''
await macos_tool.execute(action="run_applescript", script=script)
```

## Error Handling

The tools return `SmolToolResult` objects with success/error information:

```python
result = await macos_tool.execute(action="open_app", app_name="NonExistentApp")
if not result.success:
    print(f"Error: {result.error}")
else:
    print(f"Success: {result.output}")
```

## Troubleshooting

### Common Issues

1. **Accessibility Permissions**
   - Error: "AXError -25204"
   - Solution: Enable Accessibility permissions for your terminal/IDE

2. **App Not Found**
   - Error: "Failed to launch app"
   - Solution: Check app name spelling and ensure app is installed

3. **Element Not Found**
   - Error: "Invalid index"
   - Solution: Get fresh UI tree and verify element indices

4. **AppleScript Errors**
   - Error: "AppleScript execution failed"
   - Solution: Test script in Script Editor first

### Best Practices

1. **Always use try/finally blocks** to ensure cleanup
2. **Add delays** after opening apps to let them load
3. **Get fresh UI trees** before interacting with elements
4. **Test AppleScript** in Script Editor before using in automation
5. **Handle errors gracefully** and provide fallback options

## Integration with Smolagents

The macOS tools integrate seamlessly with the smolagents framework:

```python
from smolagents import CodeAgent
from smolagents_tools import create_tool

# Create agent with macOS capabilities
agent = CodeAgent(
    tools=[
        create_tool("macos"),
        create_tool("simple_macos"),
        # ... other tools
    ]
)

# Agent can now use macOS automation
result = agent.run("Open Calculator and compute 5 + 3")
```

## Security Considerations

- **Accessibility permissions** grant broad system access
- **AppleScript execution** can perform system-level operations
- **Always validate inputs** before executing scripts
- **Use least privilege principle** - only grant necessary permissions
- **Monitor automation** for unexpected behavior

## Contributing

To contribute to the macOS automation tool:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This tool is part of the smolagents-tools package and follows the same license terms.