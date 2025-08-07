"""
Web crawling tool adapted for smolagents
"""

import asyncio
from typing import Optional, List, Dict, Any
from crawl4ai import AsyncWebCrawler
from .base import AsyncSmolTool, SmolToolResult


class WebCrawlerTool(AsyncSmolTool):
    """
    A tool for web crawling and content extraction using Crawl4AI
    Adapted from OpenManus Crawl4aiTool
    """
    
    def __init__(self):
        self.name = "web_crawler"
        self.description = """A tool for crawling web pages and extracting structured content. Can extract text, links, images, and perform smart content extraction."""
        
        self.inputs = {
            "url": {
                "type": "string",
                "description": "URL to crawl",
                "required": True
            },
            "extraction_strategy": {
                "type": "string",
                "description": "Extraction strategy: basic, llm, css, xpath",
                "default": "basic",
                "required": False
            },
            "css_selector": {
                "type": "string",
                "description": "CSS selector for targeted extraction (when using css strategy)",
                "required": False
            },
            "xpath": {
                "type": "string",
                "description": "XPath expression for targeted extraction (when using xpath strategy)",
                "required": False
            },
            "word_count_threshold": {
                "type": "integer",
                "description": "Minimum word count for content blocks",
                "default": 10,
                "required": False
            },
            "only_text": {
                "type": "boolean",
                "description": "Extract only text content",
                "default": True,
                "required": False
            },
            "include_links": {
                "type": "boolean",
                "description": "Include links in extraction",
                "default": False,
                "required": False
            },
            "include_images": {
                "type": "boolean",
                "description": "Include images in extraction",
                "default": False,
                "required": False
            },
            "wait_for": {
                "type": "string",
                "description": "CSS selector to wait for before extraction",
                "required": False
            },
            "timeout": {
                "type": "integer",
                "description": "Request timeout in seconds",
                "default": 30,
                "required": False
            }
        }
        self.output_type = "string"
        super().__init__()
    
    async def _extract_with_basic_strategy(self, crawler, url: str, **kwargs) -> Dict[str, Any]:
        """Extract content using basic strategy"""
        result = await crawler.arun(
            url=url,
            word_count_threshold=kwargs.get('word_count_threshold', 10),
            only_text=kwargs.get('only_text', True),
            bypass_cache=True,
            wait_for=kwargs.get('wait_for'),
            timeout=kwargs.get('timeout', 30)
        )
        return result
    
    async def _extract_with_css_strategy(self, crawler, url: str, css_selector: str, **kwargs) -> Dict[str, Any]:
        """Extract content using CSS selector strategy"""
        from crawl4ai.extraction_strategy import CosineStrategy
        
        extraction_strategy = CosineStrategy(
            semantic_filter=css_selector,
            word_count_threshold=kwargs.get('word_count_threshold', 10)
        )
        
        result = await crawler.arun(
            url=url,
            extraction_strategy=extraction_strategy,
            bypass_cache=True,
            wait_for=kwargs.get('wait_for'),
            timeout=kwargs.get('timeout', 30)
        )
        return result
    
    async def _extract_with_llm_strategy(self, crawler, url: str, **kwargs) -> Dict[str, Any]:
        """Extract content using LLM strategy"""
        from crawl4ai.extraction_strategy import LLMExtractionStrategy
        
        extraction_strategy = LLMExtractionStrategy(
            provider="ollama/llama2",  # Default to local model
            api_token=None,
            instruction="Extract the main content and key information from this webpage."
        )
        
        result = await crawler.arun(
            url=url,
            extraction_strategy=extraction_strategy,
            bypass_cache=True,
            wait_for=kwargs.get('wait_for'),
            timeout=kwargs.get('timeout', 30)
        )
        return result
    
    async def _format_result(self, result: Dict[str, Any], include_links: bool = False, 
                           include_images: bool = False) -> str:
        """Format crawling result for output"""
        output_parts = []
        
        # Basic info
        if result.get('url'):
            output_parts.append(f"URL: {result['url']}")
        
        if result.get('title'):
            output_parts.append(f"Title: {result['title']}")
        
        # Main content
        if result.get('cleaned_html'):
            content = result['cleaned_html'][:2000]
            if len(result['cleaned_html']) > 2000:
                content += "..."
            output_parts.append(f"Content:\n{content}")
        elif result.get('markdown'):
            content = result['markdown'][:2000]
            if len(result['markdown']) > 2000:
                content += "..."
            output_parts.append(f"Content (Markdown):\n{content}")
        
        # Links
        if include_links and result.get('links'):
            links = result['links'][:10]  # Limit to first 10 links
            links_text = "\n".join([f"- {link.get('text', 'No text')}: {link.get('href', 'No URL')}" 
                                   for link in links])
            output_parts.append(f"Links:\n{links_text}")
        
        # Images
        if include_images and result.get('media'):
            images = [item for item in result['media'] if item.get('type') == 'image'][:5]
            if images:
                images_text = "\n".join([f"- {img.get('alt', 'No alt')}: {img.get('src', 'No src')}" 
                                        for img in images])
                output_parts.append(f"Images:\n{images_text}")
        
        # Extracted data
        if result.get('extracted_content'):
            extracted = str(result['extracted_content'])[:1000]
            if len(str(result['extracted_content'])) > 1000:
                extracted += "..."
            output_parts.append(f"Extracted Data:\n{extracted}")
        
        return "\n\n".join(output_parts)
    
    async def execute(self, url: str, extraction_strategy: str = "basic", 
                     css_selector: str = None, xpath: str = None,
                     word_count_threshold: int = 10, only_text: bool = True,
                     include_links: bool = False, include_images: bool = False,
                     wait_for: str = None, timeout: int = 30, **kwargs) -> SmolToolResult:
        """
        Crawl and extract content from a web page.
        
        Args:
            url (str): URL to crawl
            extraction_strategy (str): Strategy to use for extraction
            css_selector (str): CSS selector for targeted extraction
            xpath (str): XPath for targeted extraction
            word_count_threshold (int): Minimum word count for content blocks
            only_text (bool): Extract only text content
            include_links (bool): Include links in output
            include_images (bool): Include images in output
            wait_for (str): CSS selector to wait for
            timeout (int): Request timeout in seconds
            
        Returns:
            SmolToolResult: Crawling result with extracted content
        """
        try:
            async with AsyncWebCrawler(verbose=False) as crawler:
                
                if extraction_strategy == "basic":
                    result = await self._extract_with_basic_strategy(
                        crawler, url, 
                        word_count_threshold=word_count_threshold,
                        only_text=only_text,
                        wait_for=wait_for,
                        timeout=timeout
                    )
                
                elif extraction_strategy == "css":
                    if not css_selector:
                        return SmolToolResult(
                            error="css_selector is required for css extraction strategy",
                            success=False
                        )
                    result = await self._extract_with_css_strategy(
                        crawler, url, css_selector,
                        word_count_threshold=word_count_threshold,
                        wait_for=wait_for,
                        timeout=timeout
                    )
                
                elif extraction_strategy == "llm":
                    result = await self._extract_with_llm_strategy(
                        crawler, url,
                        wait_for=wait_for,
                        timeout=timeout
                    )
                
                elif extraction_strategy == "xpath":
                    if not xpath:
                        return SmolToolResult(
                            error="xpath is required for xpath extraction strategy",
                            success=False
                        )
                    # XPath strategy would need custom implementation
                    return SmolToolResult(
                        error="XPath extraction strategy not yet implemented",
                        success=False
                    )
                
                else:
                    return SmolToolResult(
                        error=f"Unknown extraction strategy: {extraction_strategy}",
                        success=False
                    )
                
                # Check if crawling was successful
                if not result.success:
                    return SmolToolResult(
                        error=f"Crawling failed: {result.error_message}",
                        success=False
                    )
                
                # Format and return result
                formatted_output = await self._format_result(
                    result.__dict__,
                    include_links=include_links,
                    include_images=include_images
                )
                
                return SmolToolResult(
                    output=formatted_output,
                    success=True,
                    artifacts={
                        "raw_html": result.html,
                        "cleaned_html": result.cleaned_html,
                        "markdown": result.markdown,
                        "links": result.links,
                        "media": result.media
                    }
                )
                
        except Exception as e:
            return SmolToolResult(
                error=f"Web crawling failed: {str(e)}",
                success=False
            )


class SimpleWebScraperTool(AsyncSmolTool):
    """Simple web scraper for basic content extraction"""
    
    def __init__(self):
        self.name = "simple_web_scraper"
        self.description = "Simple tool for extracting text content from web pages"
        
        self.inputs = {
            "url": {
                "type": "string",
                "description": "URL to scrape",
                "required": True
            },
            "format": {
                "type": "string",
                "description": "Output format: text, markdown, html",
                "default": "text",
                "required": False
            }
        }
        self.output_type = "string"
        super().__init__()
    
    async def execute(self, url: str, format: str = "text", **kwargs) -> SmolToolResult:
        """Simple web scraping"""
        try:
            async with AsyncWebCrawler(verbose=False) as crawler:
                result = await crawler.arun(
                    url=url,
                    only_text=(format == "text"),
                    bypass_cache=True
                )
                
                if not result.success:
                    return SmolToolResult(
                        error=f"Scraping failed: {result.error_message}",
                        success=False
                    )
                
                if format == "text":
                    content = result.cleaned_html or "No content extracted"
                elif format == "markdown":
                    content = result.markdown or "No markdown content"
                elif format == "html":
                    content = result.html or "No HTML content"
                else:
                    content = result.cleaned_html or "No content extracted"
                
                # Limit output size
                if len(content) > 3000:
                    content = content[:3000] + "..."
                
                return SmolToolResult(
                    output=content,
                    success=True
                )
                
        except Exception as e:
            return SmolToolResult(
                error=f"Web scraping failed: {str(e)}",
                success=False
            )