"""
Browser automation tool adapted for smolagents
"""

import asyncio
import base64
from typing import Optional, Dict, Any, List
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from .base import AsyncSmolTool, SmolToolResult


class BrowserTool(AsyncSmolTool):
    """
    A tool for browser automation using Playwright
    Adapted from OpenManus BrowserUseTool
    """
    
    def __init__(self):
        self.name = "browser"
        self.description = """A tool for browser automation. Can navigate to URLs, take screenshots, click elements, fill forms, and extract content."""
        
        self.inputs = {
            "action": {
                "type": "string",
                "description": "Action to perform: navigate, screenshot, click, fill, extract_text, scroll, wait, close",
                "required": True
            },
            "url": {
                "type": "string",
                "description": "URL to navigate to (required for 'navigate' action)",
                "required": False
            },
            "selector": {
                "type": "string",
                "description": "CSS selector for element (required for click, fill, extract_text actions)",
                "required": False
            },
            "text": {
                "type": "string",
                "description": "Text to fill in form field (required for 'fill' action)",
                "required": False
            },
            "wait_time": {
                "type": "integer",
                "description": "Time to wait in milliseconds (for 'wait' action)",
                "default": 1000,
                "required": False
            },
            "scroll_direction": {
                "type": "string",
                "description": "Direction to scroll: up, down, left, right (for 'scroll' action)",
                "default": "down",
                "required": False
            },
            "headless": {
                "type": "boolean",
                "description": "Run browser in headless mode",
                "default": True,
                "required": False
            }
        }
        self.output_type = "string"
        
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._playwright = None
        super().__init__()
    
    async def _ensure_browser(self, headless: bool = True) -> None:
        """Ensure browser is running"""
        if self._browser is None:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=headless)
            self._context = await self._browser.new_context()
            self._page = await self._context.new_page()
    
    async def _close_browser(self) -> None:
        """Close browser and cleanup"""
        if self._page:
            await self._page.close()
            self._page = None
        if self._context:
            await self._context.close()
            self._context = None
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
    
    async def _navigate(self, url: str) -> SmolToolResult:
        """Navigate to URL"""
        try:
            await self._page.goto(url, wait_until="networkidle")
            title = await self._page.title()
            return SmolToolResult(
                output=f"Successfully navigated to {url}. Page title: {title}",
                success=True
            )
        except Exception as e:
            return SmolToolResult(
                error=f"Failed to navigate to {url}: {str(e)}",
                success=False
            )
    
    async def _screenshot(self) -> SmolToolResult:
        """Take screenshot"""
        try:
            screenshot_bytes = await self._page.screenshot(full_page=True)
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode()
            
            return SmolToolResult(
                output=f"Screenshot taken successfully. Base64 data: {screenshot_b64[:100]}...",
                success=True,
                artifacts={"screenshot": screenshot_b64}
            )
        except Exception as e:
            return SmolToolResult(
                error=f"Failed to take screenshot: {str(e)}",
                success=False
            )
    
    async def _click(self, selector: str) -> SmolToolResult:
        """Click element"""
        try:
            await self._page.click(selector)
            return SmolToolResult(
                output=f"Successfully clicked element: {selector}",
                success=True
            )
        except Exception as e:
            return SmolToolResult(
                error=f"Failed to click element {selector}: {str(e)}",
                success=False
            )
    
    async def _fill(self, selector: str, text: str) -> SmolToolResult:
        """Fill form field"""
        try:
            await self._page.fill(selector, text)
            return SmolToolResult(
                output=f"Successfully filled {selector} with text",
                success=True
            )
        except Exception as e:
            return SmolToolResult(
                error=f"Failed to fill {selector}: {str(e)}",
                success=False
            )
    
    async def _extract_text(self, selector: str = None) -> SmolToolResult:
        """Extract text from element or page"""
        try:
            if selector:
                text = await self._page.text_content(selector)
                return SmolToolResult(
                    output=f"Text from {selector}: {text}",
                    success=True
                )
            else:
                text = await self._page.text_content("body")
                return SmolToolResult(
                    output=f"Page text: {text[:1000]}{'...' if len(text) > 1000 else ''}",
                    success=True
                )
        except Exception as e:
            return SmolToolResult(
                error=f"Failed to extract text: {str(e)}",
                success=False
            )
    
    async def _scroll(self, direction: str = "down") -> SmolToolResult:
        """Scroll page"""
        try:
            if direction == "down":
                await self._page.keyboard.press("PageDown")
            elif direction == "up":
                await self._page.keyboard.press("PageUp")
            elif direction == "left":
                await self._page.keyboard.press("ArrowLeft")
            elif direction == "right":
                await self._page.keyboard.press("ArrowRight")
            else:
                return SmolToolResult(
                    error=f"Invalid scroll direction: {direction}",
                    success=False
                )
            
            return SmolToolResult(
                output=f"Scrolled {direction}",
                success=True
            )
        except Exception as e:
            return SmolToolResult(
                error=f"Failed to scroll: {str(e)}",
                success=False
            )
    
    async def _wait(self, wait_time: int = 1000) -> SmolToolResult:
        """Wait for specified time"""
        try:
            await asyncio.sleep(wait_time / 1000)
            return SmolToolResult(
                output=f"Waited {wait_time}ms",
                success=True
            )
        except Exception as e:
            return SmolToolResult(
                error=f"Failed to wait: {str(e)}",
                success=False
            )
    
    async def execute(self, action: str, url: str = None, selector: str = None, 
                     text: str = None, wait_time: int = 1000, 
                     scroll_direction: str = "down", headless: bool = True, 
                     **kwargs) -> SmolToolResult:
        """
        Execute browser action.
        
        Args:
            action (str): Action to perform
            url (str): URL for navigation
            selector (str): CSS selector for element operations
            text (str): Text for form filling
            wait_time (int): Wait time in milliseconds
            scroll_direction (str): Scroll direction
            headless (bool): Run in headless mode
            
        Returns:
            SmolToolResult: Result of the browser operation
        """
        try:
            if action == "close":
                await self._close_browser()
                return SmolToolResult(
                    output="Browser closed successfully",
                    success=True
                )
            
            # Ensure browser is running for all other actions
            await self._ensure_browser(headless)
            
            if action == "navigate":
                if not url:
                    return SmolToolResult(
                        error="URL is required for navigate action",
                        success=False
                    )
                return await self._navigate(url)
            
            elif action == "screenshot":
                return await self._screenshot()
            
            elif action == "click":
                if not selector:
                    return SmolToolResult(
                        error="Selector is required for click action",
                        success=False
                    )
                return await self._click(selector)
            
            elif action == "fill":
                if not selector or not text:
                    return SmolToolResult(
                        error="Selector and text are required for fill action",
                        success=False
                    )
                return await self._fill(selector, text)
            
            elif action == "extract_text":
                return await self._extract_text(selector)
            
            elif action == "scroll":
                return await self._scroll(scroll_direction)
            
            elif action == "wait":
                return await self._wait(wait_time)
            
            else:
                return SmolToolResult(
                    error=f"Unknown action: {action}",
                    success=False
                )
                
        except Exception as e:
            return SmolToolResult(
                error=f"Browser tool error: {str(e)}",
                success=False
            )
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._close_browser()


class SimpleBrowserTool(AsyncSmolTool):
    """Simplified browser tool for basic operations"""
    
    def __init__(self):
        self.name = "simple_browser"
        self.description = "Simple browser tool for basic web operations"
        
        self.inputs = {
            "url": {
                "type": "string",
                "description": "URL to visit and extract content from",
                "required": True
            },
            "action": {
                "type": "string",
                "description": "Action to perform: content, screenshot, title",
                "default": "content",
                "required": False
            }
        }
        self.output_type = "string"
        super().__init__()
    
    async def execute(self, url: str, action: str = "content", **kwargs) -> SmolToolResult:
        """Execute simple browser operation"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                await page.goto(url, wait_until="networkidle")
                
                if action == "content":
                    content = await page.text_content("body")
                    result = SmolToolResult(
                        output=content[:2000] + ("..." if len(content) > 2000 else ""),
                        success=True
                    )
                elif action == "screenshot":
                    screenshot = await page.screenshot(full_page=True)
                    screenshot_b64 = base64.b64encode(screenshot).decode()
                    result = SmolToolResult(
                        output=f"Screenshot taken of {url}",
                        success=True,
                        artifacts={"screenshot": screenshot_b64}
                    )
                elif action == "title":
                    title = await page.title()
                    result = SmolToolResult(
                        output=f"Page title: {title}",
                        success=True
                    )
                else:
                    result = SmolToolResult(
                        error=f"Unknown action: {action}",
                        success=False
                    )
                
                await browser.close()
                return result
                
        except Exception as e:
            return SmolToolResult(
                error=f"Browser error: {str(e)}",
                success=False
            )