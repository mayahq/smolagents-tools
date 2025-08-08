#!/usr/bin/env python3
"""
Example demonstrating VNC tool with parameterized base64-encoded screenshot output
"""

import asyncio
from smolagents_tools.utils.vnc import VNCComputerUseTool

async def main():
    """Example of using VNC tool with parameterized base64 screenshot output"""
    
    # Create VNC tool instance
    vnc_tool = VNCComputerUseTool()
    
    # VNC server configuration
    vnc_host = "localhost"  # Change to your VNC server host
    vnc_port = 5900        # Change to your VNC server port
    vnc_password = None    # Set if your VNC server requires a password
    
    try:
        # Connect to VNC server
        print("Connecting to VNC server...")
        result = await vnc_tool.execute(
            action="connect",
            host=vnc_host,
            port=vnc_port,
            password=vnc_password
        )
        
        if not result.success:
            print(f"Connection failed: {result.error}")
            return
        
        print("Connected successfully!")
        
        # Example 1: Screenshot with default parameters
        print("\n1. Taking screenshot with default parameters...")
        result = await vnc_tool.execute(
            action="capture_screen",
            filename="/tmp/vnc_default.png"
        )
        
        if result.success:
            print("Screenshot captured!")
            # The output contains the file path and base64 image tag
            lines = result.output.split('\n')
            print(f"   File: {lines[0]}")
            print("   Default image tag attributes:")
            print("   - title: 'VNC Screenshot'")
            print("   - alt: 'VNC screen capture'")
            print("   - display: 'true'")
            print("   - include_in_next_call: 'true'")
        
        # Example 2: Screenshot with custom title and alt text
        print("\n2. Taking screenshot with custom title and alt...")
        result = await vnc_tool.execute(
            action="capture_screen",
            filename="/tmp/vnc_custom.png",
            img_title="Application Dashboard",
            img_alt="Screenshot of the main application dashboard showing user statistics"
        )
        
        if result.success:
            print("Screenshot captured with custom attributes!")
            lines = result.output.split('\n')
            print(f"   File: {lines[0]}")
            print("   Custom attributes applied:")
            print("   - title: 'Application Dashboard'")
            print("   - alt: 'Screenshot of the main application dashboard showing user statistics'")
        
        # Example 3: Screenshot for background processing (not displayed)
        print("\n3. Taking screenshot for background processing...")
        result = await vnc_tool.execute(
            action="capture_screen",
            filename="/tmp/vnc_background.png",
            img_title="Background Process Screenshot",
            img_alt="Screenshot for automated analysis",
            display="false",  # Don't display this screenshot
            include_in_next_call="false"  # Don't include in agent observations
        )
        
        if result.success:
            print("Background screenshot captured!")
            print("   This screenshot won't be displayed and won't be included in agent observations")
        
        # Example 4: Region capture with custom parameters
        print("\n4. Taking region screenshot with custom parameters...")
        result = await vnc_tool.execute(
            action="capture_region",
            x=100,
            y=100,
            width=800,
            height=600,
            filename="/tmp/vnc_region_custom.png",
            img_title="Login Form Region",
            img_alt="Screenshot of the login form area"
        )
        
        if result.success:
            print("Region screenshot captured!")
            print("   Note: vncdotool captures full screen, but metadata indicates the intended region")
            lines = result.output.split('\n')
            print(f"   File: {lines[0]}")
            print("   Custom region attributes applied")
        
        # Example 5: Region capture with auto-generated alt text
        print("\n5. Taking region screenshot with auto-generated alt text...")
        result = await vnc_tool.execute(
            action="capture_region",
            x=200,
            y=150,
            width=640,
            height=480,
            filename="/tmp/vnc_region_auto.png",
            img_title="Auto-Alt Region"
            # No img_alt provided - will auto-generate based on coordinates
        )
        
        if result.success:
            print("Region screenshot with auto-generated alt text captured!")
            print("   Alt text auto-generated as: 'VNC region capture at (200,150) 640x480'")
        
        # Example 6: Using the base64 image in HTML
        print("\n6. Demonstrating HTML usage...")
        result = await vnc_tool.execute(
            action="capture_screen",
            filename="/tmp/vnc_html_demo.png",
            img_title="HTML Demo Screenshot",
            img_alt="Screenshot for HTML embedding demonstration"
        )
        
        if result.success:
            lines = result.output.split('\n')
            if len(lines) > 1:
                img_tag = lines[1]
                print("The generated image tag can be directly embedded in HTML:")
                print(f"   {img_tag[:100]}...")  # Show first 100 chars
                
                # Save a sample HTML file
                html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>VNC Screenshot Demo</title>
</head>
<body>
    <h1>VNC Screenshot Embedded as Base64</h1>
    <p>This screenshot was captured using the VNC tool:</p>
    {img_tag}
</body>
</html>"""
                
                with open("/tmp/vnc_screenshot_demo.html", "w") as f:
                    f.write(html_content)
                print("   Sample HTML file saved to: /tmp/vnc_screenshot_demo.html")
        
        # Disconnect from VNC server
        print("\nDisconnecting...")
        await vnc_tool.execute(action="disconnect")
        print("Disconnected successfully!")
        
        print("\n" + "="*60)
        print("Summary of parameterized screenshot features:")
        print("- img_title: Sets the title attribute of the image tag")
        print("- img_alt: Sets the alt text (auto-generated for regions if not provided)")
        print("- display: Controls whether the image should be displayed ('true'/'false')")
        print("- include_in_next_call: Controls agent observation inclusion ('true'/'false')")
        print("="*60)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("VNC Tool Parameterized Base64 Screenshot Example")
    print("=" * 50)
    print("This example demonstrates the parameterized screenshot feature")
    print("that allows customization of title, alt text, and display options.")
    print("=" * 50)
    print()
    
    asyncio.run(main())