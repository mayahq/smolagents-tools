"""
Test cases for VNC Computer Use Tool
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

try:
    from smolagents_tools.vnc import VNCComputerUseTool, SimpleVNCComputerUseTool
    VNC_AVAILABLE = True
except ImportError:
    VNC_AVAILABLE = False


@pytest.mark.asyncio
async def test_vnc_tool_initialization():
    """Test VNC tool initialization"""
    if not VNC_AVAILABLE:
        pytest.skip("VNC tools not available")
    
    tool = VNCComputerUseTool()
    assert tool.name == "vnc_computer"
    assert tool.description is not None
    assert tool.inputs is not None
    assert tool.output_type == "string"


@pytest.mark.asyncio
async def test_simple_vnc_tool_initialization():
    """Test Simple VNC tool initialization"""
    if not VNC_AVAILABLE:
        pytest.skip("VNC tools not available")
    
    tool = SimpleVNCComputerUseTool()
    assert tool.name == "simple_vnc_computer"
    assert tool.description is not None
    assert tool.inputs is not None
    assert tool.output_type == "string"


@pytest.mark.asyncio
async def test_vnc_tool_connect_action():
    """Test VNC tool connect action"""
    if not VNC_AVAILABLE:
        pytest.skip("VNC tools not available")
    
    tool = VNCComputerUseTool()
    
    # Test missing host
    result = await tool.execute(action="connect")
    assert not result.success
    assert "host is required" in result.error


@pytest.mark.asyncio
async def test_vnc_tool_mouse_move_action():
    """Test VNC tool mouse move action"""
    if not VNC_AVAILABLE:
        pytest.skip("VNC tools not available")
    
    tool = VNCComputerUseTool()
    
    # Test without connection
    result = await tool.execute(action="mouse_move", x=100, y=100)
    assert not result.success
    assert "Not connected" in result.error


@pytest.mark.asyncio
async def test_vnc_tool_key_press_action():
    """Test VNC tool key press action"""
    if not VNC_AVAILABLE:
        pytest.skip("VNC tools not available")
    
    tool = VNCComputerUseTool()
    
    # Test without connection
    result = await tool.execute(action="key_press", key="a")
    assert not result.success
    assert "Not connected" in result.error


@pytest.mark.asyncio
async def test_vnc_tool_type_text_action():
    """Test VNC tool type text action"""
    if not VNC_AVAILABLE:
        pytest.skip("VNC tools not available")
    
    tool = VNCComputerUseTool()
    
    # Test without connection
    result = await tool.execute(action="type_text", text="hello")
    assert not result.success
    assert "Not connected" in result.error


@pytest.mark.asyncio
async def test_vnc_tool_unknown_action():
    """Test VNC tool unknown action"""
    if not VNC_AVAILABLE:
        pytest.skip("VNC tools not available")
    
    tool = VNCComputerUseTool()
    
    result = await tool.execute(action="unknown_action")
    assert not result.success
    assert "Unknown action" in result.error


@pytest.mark.asyncio
async def test_simple_vnc_tool_unknown_action():
    """Test Simple VNC tool unknown action"""
    if not VNC_AVAILABLE:
        pytest.skip("VNC tools not available")
    
    tool = SimpleVNCComputerUseTool()
    
    result = await tool.execute(action="unknown_action")
    assert not result.success
    assert "Unknown action" in result.error


if __name__ == "__main__":
    pytest.main([__file__])