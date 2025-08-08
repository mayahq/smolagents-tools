"""
Web search tool adapted for smolagents
"""

import asyncio
from typing import List, Dict, Any, Optional
from .base import AsyncSmolTool, SmolToolResult

try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class WebSearchTool(AsyncSmolTool):
    """
    A tool for web searching using multiple search engines
    Adapted from OpenManus WebSearch
    """
    
    def __init__(self):
        self.name = "web_search"
        self.description = """Search the web using various search engines (DuckDuckGo, Google, Bing). Returns search results with titles, URLs, and snippets."""
        
        self.inputs = {
            "query": {
                "type": "string",
                "description": "The search query",
                "required": True
            },
            "engine": {
                "type": "string",
                "description": "Search engine to use: duckduckgo, google, bing",
                "default": "duckduckgo",
                "required": False
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 10,
                "required": False
            },
            "region": {
                "type": "string",
                "description": "Region for search results (e.g., 'us-en', 'uk-en')",
                "default": "us-en",
                "required": False
            },
            "time_range": {
                "type": "string",
                "description": "Time range for results: d (day), w (week), m (month), y (year)",
                "required": False
            }
        }
        self.output_type = "string"
        super().__init__()
    
    async def _search_duckduckgo(self, query: str, max_results: int = 10, 
                                region: str = "us-en", time_range: str = None) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo"""
        if not DDGS_AVAILABLE:
            raise ImportError("duckduckgo-search not available. Install with: pip install duckduckgo-search")
        
        try:
            with DDGS() as ddgs:
                kwargs = {
                    "keywords": query,
                    "region": region,
                    "max_results": max_results
                }
                if time_range:
                    kwargs["timelimit"] = time_range
                
                results = list(ddgs.text(**kwargs))
                return results
        except Exception as e:
            raise Exception(f"DuckDuckGo search failed: {str(e)}")
    
    async def _search_google(self, query: str, max_results: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """Search using Google (via SerpAPI or similar)"""
        # This would require a Google API key or SerpAPI
        # For now, fall back to DuckDuckGo
        return await self._search_duckduckgo(query, max_results)
    
    async def _search_bing(self, query: str, max_results: int = 10, **kwargs) -> List[Dict[str, Any]]:
        """Search using Bing"""
        # This would require Bing API key
        # For now, fall back to DuckDuckGo
        return await self._search_duckduckgo(query, max_results)
    
    def _format_results(self, results: List[Dict[str, Any]], query: str) -> str:
        """Format search results for output"""
        if not results:
            return f"No results found for query: {query}"
        
        output = f"Search results for: {query}\n"
        output += "=" * 50 + "\n\n"
        
        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            url = result.get("href", result.get("url", "No URL"))
            snippet = result.get("body", result.get("snippet", "No description"))
            
            output += f"{i}. {title}\n"
            output += f"   URL: {url}\n"
            output += f"   Description: {snippet}\n\n"
        
        return output
    
    async def execute(self, query: str, engine: str = "duckduckgo",
                     max_results: int = 10, region: str = "us-en",
                     time_range: str = None, timeout: int = 30, **kwargs) -> SmolToolResult:
        """
        Execute web search.
        
        Args:
            query (str): Search query
            engine (str): Search engine to use
            max_results (int): Maximum results to return
            region (str): Search region
            time_range (str): Time range filter
            timeout (int): Timeout in seconds for search operations
            
        Returns:
            SmolToolResult: Search results
        """
        try:
            if engine.lower() == "duckduckgo":
                results = await self._search_duckduckgo(query, max_results, region, time_range)
            elif engine.lower() == "google":
                results = await self._search_google(query, max_results)
            elif engine.lower() == "bing":
                results = await self._search_bing(query, max_results)
            else:
                return SmolToolResult(
                    error=f"Unknown search engine: {engine}. Supported: duckduckgo, google, bing",
                    success=False
                )
            
            formatted_output = self._format_results(results, query)
            
            return SmolToolResult(
                output=formatted_output,
                success=True,
                artifacts={
                    "results": results,
                    "query": query,
                    "engine": engine,
                    "count": len(results)
                }
            )
            
        except Exception as e:
            return SmolToolResult(
                error=f"Web search failed: {str(e)}",
                success=False
            )


class DuckDuckGoSearchTool(AsyncSmolTool):
    """
    Dedicated DuckDuckGo search tool
    """
    
    def __init__(self):
        self.name = "duckduckgo_search"
        self.description = """Search the web using DuckDuckGo search engine. Returns search results with titles, URLs, and snippets."""
        
        self.inputs = {
            "query": {
                "type": "string",
                "description": "The search query",
                "required": True
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 10,
                "required": False
            },
            "region": {
                "type": "string",
                "description": "Region for search results (e.g., 'us-en', 'uk-en')",
                "default": "us-en",
                "required": False
            },
            "time_range": {
                "type": "string",
                "description": "Time range for results: d (day), w (week), m (month), y (year)",
                "required": False
            }
        }
        self.output_type = "string"
        super().__init__()
    
    async def execute(self, query: str, max_results: int = 10, 
                     region: str = "us-en", time_range: str = None, 
                     **kwargs) -> SmolToolResult:
        """Execute DuckDuckGo search"""
        web_search = WebSearchTool()
        return await web_search.execute(
            query=query,
            engine="duckduckgo",
            max_results=max_results,
            region=region,
            time_range=time_range
        )


class GoogleSearchTool(AsyncSmolTool):
    """
    Google search tool (currently falls back to DuckDuckGo)
    """
    
    def __init__(self):
        self.name = "google_search"
        self.description = """Search the web using Google search engine. Currently falls back to DuckDuckGo."""
        
        self.inputs = {
            "query": {
                "type": "string",
                "description": "The search query",
                "required": True
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 10,
                "required": False
            },
            "api_key": {
                "type": "string",
                "description": "Google API key (optional)",
                "required": False
            }
        }
        self.output_type = "string"
        super().__init__()
    
    async def execute(self, query: str, max_results: int = 10, 
                     api_key: str = None, **kwargs) -> SmolToolResult:
        """Execute Google search (falls back to DuckDuckGo)"""
        web_search = WebSearchTool()
        return await web_search.execute(
            query=query,
            engine="google",
            max_results=max_results
        )


class BingSearchTool(AsyncSmolTool):
    """
    Bing search tool (currently falls back to DuckDuckGo)
    """
    
    def __init__(self):
        self.name = "bing_search"
        self.description = """Search the web using Bing search engine. Currently falls back to DuckDuckGo."""
        
        self.inputs = {
            "query": {
                "type": "string",
                "description": "The search query",
                "required": True
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 10,
                "required": False
            },
            "api_key": {
                "type": "string",
                "description": "Bing API key (optional)",
                "required": False
            }
        }
        self.output_type = "string"
        super().__init__()
    
    async def execute(self, query: str, max_results: int = 10, 
                     api_key: str = None, **kwargs) -> SmolToolResult:
        """Execute Bing search (falls back to DuckDuckGo)"""
        web_search = WebSearchTool()
        return await web_search.execute(
            query=query,
            engine="bing",
            max_results=max_results
        )