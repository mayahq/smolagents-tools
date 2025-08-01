"""
Web Automation Agent Example using smolagents CodeAgent with our adapted tools

This example demonstrates how to use our smolagents-tools with CodeAgent
to perform web automation tasks similar to the official smolagents examples.
"""

import os
import asyncio
from typing import Optional

# Import smolagents components
try:
    from smolagents import CodeAgent, InferenceClientModel, tool
    SMOLAGENTS_AVAILABLE = True
except ImportError:
    print("⚠️  Smolagents not installed. Install with: pip install smolagents")
    SMOLAGENTS_AVAILABLE = False

# Import our adapted tools
from smolagents_tools import (
    BashTool, WebSearchTool, BrowserTool, SimpleBrowserTool,
    FileEditorTool, PythonExecutorTool, create_web_toolset
)


def setup_model(model_id: str = "Qwen/Qwen2.5-Coder-32B-Instruct") -> Optional[InferenceClientModel]:
    """Setup the model for the agent"""
    if not SMOLAGENTS_AVAILABLE:
        return None
    
    try:
        model = InferenceClientModel(model_id=model_id)
        return model
    except Exception as e:
        print(f"⚠️  Could not initialize model {model_id}: {e}")
        print("Make sure you have the required API keys set up.")
        return None


@tool
def search_and_summarize(query: str, max_results: int = 5) -> str:
    """
    Search the web and provide a summary of results.
    
    Args:
        query: The search query
        max_results: Maximum number of results to include
    
    Returns:
        A formatted summary of search results
    """
    # Use our WebSearchTool
    search_tool = WebSearchTool()
    
    # Run the search (we need to handle async in sync context)
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're in an async context, use thread pool
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, search_tool.execute(query=query, max_results=max_results))
                result = future.result()
        else:
            result = loop.run_until_complete(search_tool.execute(query=query, max_results=max_results))
    except RuntimeError:
        result = asyncio.run(search_tool.execute(query=query, max_results=max_results))
    
    if result.success:
        return f"Search Results Summary:\n{result.output}"
    else:
        return f"Search failed: {result.error}"


@tool
def get_website_content(url: str) -> str:
    """
    Get the text content of a website.
    
    Args:
        url: The URL to fetch content from
    
    Returns:
        The text content of the website
    """
    # Use our SimpleBrowserTool
    browser_tool = SimpleBrowserTool()
    
    # Run the browser tool
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, browser_tool.execute(url=url, action="content"))
                result = future.result()
        else:
            result = loop.run_until_complete(browser_tool.execute(url=url, action="content"))
    except RuntimeError:
        result = asyncio.run(browser_tool.execute(url=url, action="content"))
    
    if result.success:
        return f"Website Content:\n{result.output}"
    else:
        return f"Failed to get content: {result.error}"


@tool
def execute_python_code(code: str) -> str:
    """
    Execute Python code safely.
    
    Args:
        code: The Python code to execute
    
    Returns:
        The output of the code execution
    """
    # Use our PythonExecutorTool
    python_tool = PythonExecutorTool()
    
    # Run the Python code
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, python_tool.execute(code=code))
                result = future.result()
        else:
            result = loop.run_until_complete(python_tool.execute(code=code))
    except RuntimeError:
        result = asyncio.run(python_tool.execute(code=code))
    
    if result.success:
        return f"Python Output:\n{result.output}"
    else:
        return f"Python execution failed: {result.error}"


def create_web_research_agent(model_id: str = "Qwen/Qwen2.5-Coder-32B-Instruct") -> Optional[CodeAgent]:
    """Create a CodeAgent configured for web research tasks"""
    if not SMOLAGENTS_AVAILABLE:
        print("❌ Smolagents not available. Cannot create agent.")
        return None
    
    model = setup_model(model_id)
    if not model:
        return None
    
    # Create agent with our custom tools
    tools = [search_and_summarize, get_website_content, execute_python_code]
    
    agent = CodeAgent(
        tools=tools,
        model=model,
        add_base_tools=True,  # Add default smolagents tools
        max_steps=15,
        verbosity_level=2
    )
    
    return agent


def create_web_automation_agent(model_id: str = "Qwen/Qwen2.5-Coder-32B-Instruct") -> Optional[CodeAgent]:
    """Create a CodeAgent configured for web automation using our tool collection"""
    if not SMOLAGENTS_AVAILABLE:
        print("❌ Smolagents not available. Cannot create agent.")
        return None
    
    model = setup_model(model_id)
    if not model:
        return None
    
    # Use our web toolset
    web_tools = create_web_toolset()
    
    # Convert our tools to the format expected by CodeAgent
    # Note: CodeAgent expects tools with forward() methods, which our tools have
    agent = CodeAgent(
        tools=web_tools,
        model=model,
        add_base_tools=True,
        max_steps=20,
        verbosity_level=2
    )
    
    return agent


def demo_web_research():
    """Demonstrate web research capabilities"""
    print("🔍 Web Research Agent Demo")
    print("=" * 50)
    
    agent = create_web_research_agent()
    if not agent:
        print("❌ Could not create agent. Skipping demo.")
        return
    
    # Example research task
    research_task = """
    I want to learn about the latest developments in AI agents. 
    Please search for recent information about AI agents, 
    summarize the key findings, and provide insights about current trends.
    """
    
    try:
        print("🤖 Running research task...")
        result = agent.run(research_task)
        print("\n📊 Research Results:")
        print(result)
    except Exception as e:
        print(f"❌ Research task failed: {e}")


def demo_website_analysis():
    """Demonstrate website content analysis"""
    print("\n🌐 Website Analysis Demo")
    print("=" * 50)
    
    agent = create_web_research_agent()
    if not agent:
        print("❌ Could not create agent. Skipping demo.")
        return
    
    # Example website analysis task
    analysis_task = """
    Please visit the Hugging Face homepage (https://huggingface.co) 
    and provide a summary of what the company does based on the content you find.
    Focus on their main products and services.
    """
    
    try:
        print("🤖 Running website analysis...")
        result = agent.run(analysis_task)
        print("\n📄 Analysis Results:")
        print(result)
    except Exception as e:
        print(f"❌ Analysis task failed: {e}")


def demo_data_processing():
    """Demonstrate data processing with Python"""
    print("\n🐍 Data Processing Demo")
    print("=" * 50)
    
    agent = create_web_research_agent()
    if not agent:
        print("❌ Could not create agent. Skipping demo.")
        return
    
    # Example data processing task
    processing_task = """
    Please search for information about the top 3 programming languages in 2024,
    then create a Python script that processes this information and creates
    a simple comparison showing their popularity or key features.
    """
    
    try:
        print("🤖 Running data processing task...")
        result = agent.run(processing_task)
        print("\n📈 Processing Results:")
        print(result)
    except Exception as e:
        print(f"❌ Processing task failed: {e}")


def demo_interactive_mode():
    """Interactive mode for custom tasks"""
    print("\n💬 Interactive Mode")
    print("=" * 50)
    print("Enter your web automation task (or 'quit' to exit):")
    
    agent = create_web_research_agent()
    if not agent:
        print("❌ Could not create agent. Exiting interactive mode.")
        return
    
    while True:
        try:
            task = input("\n🤖 Your task: ").strip()
            if task.lower() in ['quit', 'exit', 'q']:
                break
            
            if not task:
                continue
            
            print("🔄 Processing your request...")
            result = agent.run(task)
            print(f"\n✅ Result:\n{result}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def test_tool_compatibility():
    """Test that our tools work with smolagents"""
    print("🧪 Testing Tool Compatibility")
    print("=" * 50)
    
    if not SMOLAGENTS_AVAILABLE:
        print("❌ Smolagents not available. Cannot test compatibility.")
        return False
    
    try:
        # Test that our tools can be used with CodeAgent
        web_tools = create_web_toolset()
        print(f"✅ Created web toolset with {len(web_tools)} tools")
        
        # Test individual tool forward methods
        bash_tool = BashTool()
        result = bash_tool.forward(command="echo 'Tool compatibility test'")
        print(f"✅ BashTool forward method: {result}")
        
        python_tool = PythonExecutorTool()
        result = python_tool.forward(code="print('Python tool test')")
        print(f"✅ PythonExecutorTool forward method: {result}")
        
        print("✅ All compatibility tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Compatibility test failed: {e}")
        return False


def main():
    """Main function to run the examples"""
    print("🚀 Smolagents Tools - Web Automation Agent Examples")
    print("=" * 60)
    
    # Check if smolagents is available
    if not SMOLAGENTS_AVAILABLE:
        print("❌ This example requires smolagents to be installed.")
        print("Install with: pip install smolagents")
        return
    
    # Test tool compatibility first
    if not test_tool_compatibility():
        print("❌ Tool compatibility test failed. Exiting.")
        return
    
    print("\nChoose a demo to run:")
    print("1. Web Research Demo")
    print("2. Website Analysis Demo") 
    print("3. Data Processing Demo")
    print("4. Interactive Mode")
    print("5. Run All Demos")
    
    try:
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            demo_web_research()
        elif choice == "2":
            demo_website_analysis()
        elif choice == "3":
            demo_data_processing()
        elif choice == "4":
            demo_interactive_mode()
        elif choice == "5":
            demo_web_research()
            demo_website_analysis()
            demo_data_processing()
        else:
            print("❌ Invalid choice. Please run the script again.")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()