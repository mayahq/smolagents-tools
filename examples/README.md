# Smolagents Tools Examples

This directory contains examples demonstrating how to use our OpenManus-adapted tools with the smolagents framework.

## 📋 Prerequisites

### Required Installations

```bash
# Install smolagents
pip install smolagents

# Install our tools (from project root)
PYTHONPATH=/path/to/smoltools python examples/your_script.py
# OR install in development mode
pip install -e .
```

### API Keys Setup

To run the CodeAgent examples, you'll need API access to language models. Set up one of the following:

#### Option 1: Hugging Face Inference API (Recommended)
```bash
# Get your token from https://huggingface.co/settings/tokens
export HUGGINGFACE_API_TOKEN="your_token_here"

# Or login via CLI
huggingface-cli login
```

#### Option 2: OpenAI API
```bash
export OPENAI_API_KEY="your_openai_key_here"
```

#### Option 3: AWS Bedrock
```bash
# Install boto3
pip install boto3

# Configure AWS credentials (choose one):
# a) AWS CLI
aws configure

# b) Environment variables
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_DEFAULT_REGION="us-east-2"

# c) IAM roles (for EC2/Lambda)
# d) AWS credentials file (~/.aws/credentials)
```

#### Option 4: Local Models
You can also use local models with Ollama or other local inference servers.

## 🚀 Available Examples

### 1. Basic Usage (`basic_usage.py`)
Demonstrates individual tool usage without CodeAgent:
```bash
PYTHONPATH=/path/to/smoltools python examples/basic_usage.py
```

**Features:**
- Individual tool testing
- Async tool execution
- Tool collections and convenience functions
- Forward method compatibility testing

### 2. CodeAgent Demo (`smolagents_codeagent_demo.py`)
Shows integration with smolagents CodeAgent:
```bash
PYTHONPATH=/path/to/smoltools python examples/smolagents_codeagent_demo.py
```

**Features:**
- Web search and analysis
- Code execution and file operations
- Mixed workflows combining multiple tools
- Interactive mode for custom tasks

### 3. Web Automation Agent (`web_automation_agent.py`)
Advanced web automation examples:
```bash
PYTHONPATH=/path/to/smoltools python examples/web_automation_agent.py
```

**Features:**
- Web research automation
- Website content analysis
- Data processing workflows
- Custom tool creation with `@tool` decorator

### 4. AWS Bedrock Example (`bedrock_example.py`) 🆕
Demonstrates AWS Bedrock integration with cross-region inference:
```bash
PYTHONPATH=/path/to/smoltools python examples/bedrock_example.py
```

**Features:**
- AWS Bedrock model integration
- Cross-region inference testing
- Multiple model support (Claude, Llama, Titan, Mistral)
- CodeAgent integration examples
- Comprehensive setup guide

## 🛠️ Example Usage Patterns

### Using Individual Tools
```python
from smolagents_tools import BashTool, WebSearchTool, PythonExecutorTool

# Direct tool usage
bash_tool = BashTool()
result = bash_tool.forward(command="echo 'Hello World'")

# Async tool usage
import asyncio
search_tool = WebSearchTool()
result = asyncio.run(search_tool.execute(query="AI news", max_results=5))
```

### Using with CodeAgent
```python
from smolagents import CodeAgent, InferenceClientModel
from smolagents_tools import create_basic_toolset

# Setup model
model = InferenceClientModel(model_id="Qwen/Qwen2.5-Coder-32B-Instruct")

# Create agent with our tools
tools = create_basic_toolset()
agent = CodeAgent(tools=tools, model=model, add_base_tools=True)

# Run tasks
result = agent.run("Search for Python tutorials and create a summary")
```

### Using AWS Bedrock
```python
from smolagents_tools import ChatCompletionTool
import asyncio

# Basic Bedrock usage
chat_tool = ChatCompletionTool()
result = asyncio.run(chat_tool.execute(
    messages="Hello, how are you?",
    provider="bedrock",
    model="anthropic.claude-3-sonnet-20240229-v1:0",
    region="us-east-1"
))

# Cross-region inference
result = asyncio.run(chat_tool.execute(
    messages="Analyze this data for insights",
    provider="bedrock",
    model="anthropic.claude-3-sonnet-20240229-v1:0",
    region="eu-west-1"  # Different region
))
```

### Creating Custom Tools
```python
from smolagents import tool
from smolagents_tools import WebSearchTool
import asyncio

@tool
def search_and_summarize(query: str, max_results: int = 5) -> str:
    """Search the web and provide a summary"""
    search_tool = WebSearchTool()
    result = asyncio.run(search_tool.execute(query=query, max_results=max_results))
    return result.output if result.success else f"Search failed: {result.error}"
```

## 🔧 Tool Collections

Our package provides several pre-configured tool collections:

### Basic Toolset
```python
from smolagents_tools import create_basic_toolset
tools = create_basic_toolset()
# Includes: bash, python_executor, file_editor, web_search, simple_browser
```

### Web Toolset
```python
from smolagents_tools import create_web_toolset
tools = create_web_toolset()
# Includes: web_search, web_crawler, browser, simple_web_scraper
```

### Development Toolset
```python
from smolagents_tools import create_development_toolset
tools = create_development_toolset()
# Includes: bash, python_executor, file_editor, file_reader, file_writer, web_search, planning
```

### AI Toolset
```python
from smolagents_tools import create_ai_toolset
tools = create_ai_toolset()
# Includes: chat_completion, simple_prompt, web_search, planning, file_editor
```

## 🎯 Example Tasks

Here are some example tasks you can try with the CodeAgent:

### Web Research
```
"Search for the latest developments in quantum computing and create a summary report"
```

### Data Analysis
```
"Create a Python script that analyzes the top programming languages of 2024, 
generate some sample data, and create visualizations"
```

### File Operations
```
"Create a project structure for a Python web application, including proper 
directory structure and basic configuration files"
```

### Mixed Workflow
```
"Research the best practices for API design, then create a sample Python 
FastAPI application demonstrating these practices"
```

### AWS Bedrock Tasks
```
"Use AWS Bedrock Claude model to analyze this business proposal and provide 
strategic recommendations with cross-region inference for reliability"
```

## 🌍 AWS Bedrock Models & Regions

### Popular Bedrock Models
- **Claude 3 Haiku**: `anthropic.claude-3-haiku-20240307-v1:0` (Fast, cost-effective)
- **Claude 3 Sonnet**: `anthropic.claude-3-sonnet-20240229-v1:0` (Balanced performance)
- **Claude 3 Opus**: `anthropic.claude-3-opus-20240229-v1:0` (Most capable)
- **Claude 3.5 Sonnet**: `anthropic.claude-3-5-sonnet-20240620-v1:0` (Latest)
- **Claude 3.7 Sonnet**: `us.anthropic.claude-3-7-sonnet-20250219-v1:0` (Newest, US region)
- **Llama 3.1 8B**: `meta.llama3-1-8b-instruct-v1:0`
- **Llama 3.1 70B**: `meta.llama3-1-70b-instruct-v1:0`
- **Titan Text**: `amazon.titan-text-express-v1`
- **Mistral 7B**: `mistral.mistral-7b-instruct-v0:2`

### Supported Regions
- `us-east-1` (N. Virginia)
- `us-west-2` (Oregon)
- `eu-west-1` (Ireland)
- `eu-central-1` (Frankfurt)
- `ap-southeast-1` (Singapore)
- `ap-northeast-1` (Tokyo)
- `ca-central-1` (Canada)
- `ap-southeast-2` (Sydney)

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Make sure PYTHONPATH is set
   export PYTHONPATH=/path/to/smoltools:$PYTHONPATH
   ```

2. **API Key Issues**
   ```bash
   # Check if your API key is set
   echo $HUGGINGFACE_API_TOKEN
   
   # Or login via CLI
   huggingface-cli login
   ```

3. **AWS Bedrock Issues**
   ```bash
   # Check AWS credentials
   aws sts get-caller-identity
   
   # Check Bedrock model access
   aws bedrock list-foundation-models --region us-east-1
   ```

4. **Model Access Issues**
   ```python
   # Try a different model
   model = InferenceClientModel(model_id="microsoft/DialoGPT-medium")
   ```

5. **Tool Compatibility**
   ```python
   # Test individual tools first
   from smolagents_tools import BashTool
   tool = BashTool()
   result = tool.forward(command="echo 'test'")
   print(result)
   ```

### AWS Bedrock Specific Issues

1. **Model Access Denied**
   - Go to AWS Bedrock console → Model access
   - Request access to the desired models
   - Wait for approval (usually instant)

2. **Region Not Supported**
   - Check if your region supports Bedrock
   - Use a supported region like `us-east-1`

3. **IAM Permissions**
   - Ensure your AWS credentials have:
     - `bedrock:InvokeModel`
     - `bedrock:InvokeModelWithResponseStream`

### Getting Help

- Check the main project README for installation instructions
- Run the test suite: `python test_installation.py`
- Try the basic usage example first: `python examples/basic_usage.py`
- For AWS Bedrock: `python examples/bedrock_example.py`
- For smolagents-specific issues, check the [official documentation](https://huggingface.co/docs/smolagents)

## 📚 Additional Resources

- [Smolagents Documentation](https://huggingface.co/docs/smolagents)
- [Smolagents Examples](https://huggingface.co/docs/smolagents/examples/web_browser)
- [Tool Creation Guide](https://huggingface.co/docs/smolagents/tutorials/tools)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [OpenManus Original Tools](https://github.com/aymeric-roucher/OpenManus)

## 🤝 Contributing

If you create interesting examples or find issues, please contribute back to the project!