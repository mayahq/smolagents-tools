# smolagents-tools

[![PyPI](https://img.shields.io/pypi/v/smolagents-tools.svg)](https://pypi.org/project/smolagents-tools/)
[![Tests](https://github.com/yourusername/smolagents-tools/actions/workflows/test.yml/badge.svg)](https://github.com/yourusername/smolagents-tools/actions/workflows/test.yml)
[![Changelog](https://img.shields.io/github/v/release/yourusername/smolagents-tools?include_prereleases&label=changelog)](https://github.com/yourusername/smolagents-tools/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/yourusername/smolagents-tools/blob/main/LICENSE)

Comprehensive collection of tools adapted from OpenManus for smolagents CodeAct loop

## 🚀 Quick Start

### Installation

```bash
# Install the base package
pip install smolagents-tools

# Install with specific feature sets
pip install smolagents-tools[search]     # Web search capabilities
pip install smolagents-tools[browser]    # Browser automation
pip install smolagents-tools[crawler]    # Web crawling
pip install smolagents-tools[macos]      # macOS automation (macOS only)
pip install smolagents-tools[llm]        # LLM integrations
pip install smolagents-tools[all]        # All features

# For development
pip install smolagents-tools[dev]
```

### Basic Usage

```python
from smolagents_tools import BashTool, WebSearchTool, PythonExecutorTool
from smolagents_tools import create_basic_toolset

# Use individual tools
bash_tool = BashTool()
result = bash_tool.forward(command="echo 'Hello World'")

# Use with smolagents CodeAgent
from smolagents import CodeAgent, InferenceClientModel

model = InferenceClientModel(model_id="Qwen/Qwen2.5-Coder-32B-Instruct")
tools = create_basic_toolset()
agent = CodeAgent(tools=tools, model=model, add_base_tools=True)

result = agent.run("Search for Python tutorials and create a summary")
```

## 🛠️ Available Tools

### Core Tools (10 main tools)
- **BashTool** - Command execution with proper error handling
- **WebSearchTool** - Multi-engine web search (DuckDuckGo, Google, Bing)
- **PythonExecutorTool** - Safe Python code execution with timeout
- **FileEditorTool** - Comprehensive file operations (view, create, edit, undo)
- **BrowserTool** - Web automation using Playwright
- **WebCrawlerTool** - Advanced web crawling with Crawl4AI
- **MacOSUseTool** - macOS application automation and UI interaction
- **SimpleMacOSTool** - Basic macOS operations and AppleScript execution
- **PlanningTool** - Task planning and management
- **ChatCompletionTool** - LLM integration (OpenAI, Anthropic, local)

### Tool Collections
- **Basic Toolset** (5 tools): Essential tools for most tasks
- **Web Toolset** (4 tools): Web-focused operations
- **Development Toolset** (7 tools): Software development workflow
- **AI Toolset** (5 tools): AI and language model integration

**Total: 19 available tools** ready for use with smolagents!

## 📚 Examples

### Individual Tool Usage
```python
# Test individual tools
from smolagents_tools import WebSearchTool
import asyncio

search_tool = WebSearchTool()
result = asyncio.run(search_tool.execute(query="AI news", max_results=5))
print(result.output)
```

### CodeAgent Integration
```python
# Interactive mode with CodeAgent
from smolagents import CodeAgent, InferenceClientModel
from smolagents_tools import create_basic_toolset

model = InferenceClientModel(model_id="Qwen/Qwen2.5-Coder-32B-Instruct")
tools = create_basic_toolset()
agent = CodeAgent(tools=tools, model=model)

# Example tasks
agent.run("Search for the latest AI developments and summarize them")
agent.run("Create a Python script that analyzes data and saves results to a file")
agent.run("Research Python best practices and create a demo application")
```

### Web Automation
```python
# Custom tool creation
from smolagents import tool
from smolagents_tools import WebSearchTool

@tool
def research_topic(topic: str) -> str:
    """Research a topic and provide insights"""
    search_tool = WebSearchTool()
    result = asyncio.run(search_tool.execute(query=topic, max_results=5))
    return f"Research on {topic}:\n{result.output}"
```

### macOS Automation (macOS only)
```python
# Basic macOS operations
from smolagents_tools import create_tool
import asyncio

async def macos_example():
    # Simple macOS tool for basic operations
    simple_tool = create_tool("simple_macos")
    
    # Text-to-speech
    result = await simple_tool.execute(
        action="say_text",
        text="Hello from macOS automation!"
    )
    
    # Open applications
    result = await simple_tool.execute(
        action="open_app",
        app_name="Calculator"
    )

asyncio.run(macos_example())
```

## 🔧 Key Features

### ✅ **Smolagents Compatibility**
- **Dynamic Forward Methods**: Automatically generated method signatures
- **Async-to-Sync Conversion**: Seamless integration with CodeAgent
- **Event Loop Handling**: Robust nested event loop management
- **Input Validation**: Proper nullable parameter handling

### ✅ **Comprehensive Tool Suite**
- **Command Execution**: Bash commands with error handling
- **Web Operations**: Search, crawling, browser automation
- **File Management**: Create, edit, view files with undo support
- **Code Execution**: Safe Python execution with timeout
- **AI Integration**: Multiple LLM providers support

### ✅ **Developer Experience**
- **Tool Registry**: Easy tool discovery and instantiation
- **Pre-configured Collections**: Ready-to-use tool sets
- **Comprehensive Testing**: 100% test pass rate
- **Rich Examples**: Multiple usage patterns demonstrated

## 🧪 Testing

```bash
# Install in development mode
pip install -e '.[dev]'

# Run tests
python -m pytest

# Run the demo
smolagents-tools-demo
```

## 🎯 Use Cases

### Research and Analysis
```python
agent.run("""
Search for recent developments in quantum computing, 
analyze the key trends, and create a comprehensive report 
with code examples demonstrating quantum concepts.
""")
```

### Web Development
```python
agent.run("""
Research modern web development best practices,
create a sample FastAPI application structure,
and include proper testing and documentation.
""")
```

### Data Science
```python
agent.run("""
Find datasets about climate change, create a Python script
to analyze the data, generate visualizations, and 
summarize the key findings in a report.
""")
```

### Automation
```python
agent.run("""
Create a script that monitors a website for changes,
sends notifications when updates are detected,
and logs all activities to a file.
""")
```

## 🔑 API Keys Setup

For CodeAgent examples, you'll need API access:

```bash
# Hugging Face (Recommended)
export HUGGINGFACE_API_TOKEN="your_token_here"

# OpenAI (Alternative)
export OPENAI_API_KEY="your_openai_key_here"

# Or login via CLI
huggingface-cli login
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Add New Tools**: Adapt more OpenManus tools
2. **Improve Examples**: Create more usage demonstrations
3. **Fix Issues**: Report and fix bugs
4. **Documentation**: Improve guides and examples

## Development

To contribute to this library, first checkout the code. Then create a new virtual environment:
```bash
cd smolagents-tools
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
python -m pip install -e '.[dev]'
```
To run the tests:
```bash
python -m pytest
```

## 📄 License

This project adapts tools from [OpenManus](https://github.com/aymeric-roucher/OpenManus) for use with [smolagents](https://github.com/huggingface/smolagents).

Licensed under the Apache License, Version 2.0.

## 🙏 Acknowledgments

- **OpenManus**: Original tool implementations
- **Smolagents**: Framework for agent-based automation
- **Hugging Face**: Infrastructure and model access

## 🔗 Links

- [Smolagents Documentation](https://huggingface.co/docs/smolagents)
- [OpenManus Repository](https://github.com/aymeric-roucher/OpenManus)
- [PyPI Package](https://pypi.org/project/smolagents-tools/)

---

**Ready to build powerful AI agents with comprehensive tool capabilities!** 🚀
