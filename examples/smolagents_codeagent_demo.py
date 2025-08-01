"""
Smolagents CodeAgent Demo with AWS Bedrock

This example demonstrates how to use our smolagents-tools with CodeAgent
using AWS Bedrock Claude 3.7 Sonnet model via LiteLLM for inference.
Requires AWS credentials and Bedrock access.
"""

import os
import sys

# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import smolagents components
try:
    from smolagents import CodeAgent, LiteLLMModel, tool
    SMOLAGENTS_AVAILABLE = True
    print("✅ Smolagents is available")
except ImportError:
    print("❌ Smolagents not installed. Install with: pip install smolagents")
    SMOLAGENTS_AVAILABLE = False

# Import our adapted tools
from smolagents_tools import (
    BashTool, WebSearchTool, PythonExecutorTool, FileEditorTool,
    create_basic_toolset, create_web_toolset
)

# Check for litellm
try:
    import litellm
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False


def setup_model():
    """Setup the model for the agent"""
    if not SMOLAGENTS_AVAILABLE:
        return None
    
    if not LITELLM_AVAILABLE:
        print("❌ litellm not available. Install with: pip install litellm")
        return None
    
    # Use AWS Bedrock Claude 3.7 Sonnet model via LiteLLM
    model_id = "bedrock/us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    
    try:
        model = LiteLLMModel(model_id=model_id)
        print(f"✅ Bedrock model {model_id} initialized successfully")
        return model
    except Exception as e:
        print(f"❌ Could not initialize Bedrock model {model_id}: {e}")
        print("💡 Make sure you have AWS credentials configured and Bedrock access enabled.")
        print("💡 Also ensure you have litellm installed: pip install litellm")
        return None


def demo_basic_web_search():
    """Demo: Basic web search and analysis"""
    print("\n🔍 Demo: Web Search and Analysis")
    print("=" * 50)
    
    if not SMOLAGENTS_AVAILABLE:
        print("❌ Smolagents not available. Skipping demo.")
        return
    
    model = setup_model()
    if not model:
        print("❌ Could not setup model. Skipping demo.")
        return
    
    # Create agent with our web tools
    web_tools = create_web_toolset()
    agent = CodeAgent(
        tools=web_tools,
        model=model,
        add_base_tools=True,
        max_steps=10,
        verbosity_level=2
    )
    
    # Task: Search and summarize
    task = """
    Search for "latest AI developments 2024" and provide a brief summary 
    of the top 3 most interesting findings. Focus on practical applications.
    """
    
    try:
        print("🤖 Agent is working on the task...")
        result = agent.run(task)
        print(f"\n✅ Task completed!\n{result}")
    except Exception as e:
        print(f"❌ Task failed: {e}")


def demo_code_execution():
    """Demo: Python code execution and file operations"""
    print("\n🐍 Demo: Code Execution and File Operations")
    print("=" * 50)
    
    if not SMOLAGENTS_AVAILABLE:
        print("❌ Smolagents not available. Skipping demo.")
        return
    
    model = setup_model()
    if not model:
        print("❌ Could not setup model. Skipping demo.")
        return
    
    # Create agent with development tools
    dev_tools = [
        PythonExecutorTool(),
        FileEditorTool(),
        BashTool()
    ]
    
    agent = CodeAgent(
        tools=dev_tools,
        model=model,
        add_base_tools=True,
        max_steps=15,
        verbosity_level=2
    )
    
    # Task: Create and analyze data
    task = """
    Create a Python script that:
    1. Generates a list of 10 random numbers between 1 and 100
    2. Calculates their mean, median, and standard deviation
    3. Saves the results to a file called 'stats_results.txt'
    4. Shows me the contents of the file
    
    Execute the script and show me the results.
    """
    
    try:
        print("🤖 Agent is working on the task...")
        result = agent.run(task)
        print(f"\n✅ Task completed!\n{result}")
    except Exception as e:
        print(f"❌ Task failed: {e}")


def demo_mixed_workflow():
    """Demo: Mixed workflow combining web search, code, and file operations"""
    print("\n🔄 Demo: Mixed Workflow")
    print("=" * 50)
    
    if not SMOLAGENTS_AVAILABLE:
        print("❌ Smolagents not available. Skipping demo.")
        return
    
    model = setup_model()
    if not model:
        print("❌ Could not setup model. Skipping demo.")
        return
    
    # Create agent with all our basic tools
    tools = create_basic_toolset()
    agent = CodeAgent(
        tools=tools,
        model=model,
        add_base_tools=True,
        max_steps=20,
        verbosity_level=2
    )
    
    # Complex task combining multiple capabilities
    task = """
    I want to learn about Python's popularity. Please:
    
    1. Search for recent information about Python programming language popularity
    2. Create a Python script that demonstrates why Python is popular by showing:
       - A simple data analysis example
       - A basic web scraping concept (just the logic, no actual scraping)
       - A machine learning example using basic math
    3. Save this demonstration script to a file called 'python_popularity_demo.py'
    4. Run the script and show me the output
    5. Create a summary report of your findings in a file called 'python_report.txt'
    
    Make it educational and fun!
    """
    
    try:
        print("🤖 Agent is working on the complex task...")
        result = agent.run(task)
        print(f"\n✅ Complex task completed!\n{result}")
    except Exception as e:
        print(f"❌ Task failed: {e}")


def test_tool_forward_methods():
    """Test that our tools work correctly with smolagents forward() interface"""
    print("\n🧪 Testing Tool Forward Methods")
    print("=" * 50)
    
    # Test BashTool
    print("Testing BashTool...")
    bash_tool = BashTool()
    result = bash_tool.forward(command="echo 'Hello from BashTool!'")
    print(f"BashTool result: {result}")
    
    # Test PythonExecutorTool
    print("\nTesting PythonExecutorTool...")
    python_tool = PythonExecutorTool()
    result = python_tool.forward(code="print('Hello from PythonExecutorTool!')")
    print(f"PythonExecutorTool result: {result}")
    
    # Test WebSearchTool
    print("\nTesting WebSearchTool...")
    search_tool = WebSearchTool()
    result = search_tool.forward(query="smolagents tutorial", max_results=2)
    print(f"WebSearchTool result: {result[:200]}...")
    
    print("\n✅ All forward methods working correctly!")


def interactive_mode():
    """Interactive mode for custom tasks"""
    print("\n💬 Interactive Mode")
    print("=" * 50)
    print("Enter your task for the agent (or 'quit' to exit):")
    print("The agent has access to web search, Python execution, file operations, and bash commands.")
    
    if not SMOLAGENTS_AVAILABLE:
        print("❌ Smolagents not available. Cannot start interactive mode.")
        return
    
    model = setup_model()
    if not model:
        print("❌ Could not setup model. Cannot start interactive mode.")
        return
    
    # Create agent with all tools
    tools = create_basic_toolset()
    agent = CodeAgent(
        tools=tools,
        model=model,
        add_base_tools=True,
        max_steps=25,
        verbosity_level=2
    )
    
    print(f"\n🤖 Agent ready with {len(tools)} tools!")
    
    while True:
        try:
            task = input("\n📝 Your task: ").strip()
            if task.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not task:
                continue
            
            print("🔄 Agent is working...")
            result = agent.run(task)
            print(f"\n✅ Result:\n{result}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main function"""
    print("🚀 Smolagents CodeAgent Demo with AWS Bedrock")
    print("=" * 60)
    print("This demo shows how to use AWS Bedrock Claude 3.7 Sonnet with smolagents CodeAgent")
    
    # Check prerequisites
    if not SMOLAGENTS_AVAILABLE:
        print("\n❌ Smolagents is not installed.")
        print("To run the full demos, install smolagents:")
        print("pip install smolagents")
        return
    
    if not LITELLM_AVAILABLE:
        print("\n❌ litellm is not installed.")
        print("To use Bedrock, install litellm:")
        print("pip install litellm")
        return
    
    # Check AWS credentials
    try:
        import boto3
        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials is None:
            print("\n❌ AWS credentials not configured.")
            print("Please configure AWS credentials before running Bedrock demos.")
            print("Use: aws configure")
            return
        else:
            print(f"\n✅ AWS credentials configured for region: {session.region_name or 'default'}")
    except Exception as e:
        print(f"\n❌ AWS configuration error: {e}")
        return
    
    # First test that our tools work
    test_tool_forward_methods()
    
    print("\nAvailable demos:")
    print("1. Basic Web Search and Analysis")
    print("2. Code Execution and File Operations")
    print("3. Mixed Workflow (Complex Task)")
    print("4. Interactive Mode")
    print("5. Run All Demos")
    
    try:
        choice = input("\nChoose a demo (1-5): ").strip()
        
        if choice == "1":
            demo_basic_web_search()
        elif choice == "2":
            demo_code_execution()
        elif choice == "3":
            demo_mixed_workflow()
        elif choice == "4":
            interactive_mode()
        elif choice == "5":
            demo_basic_web_search()
            demo_code_execution()
            demo_mixed_workflow()
        else:
            print("❌ Invalid choice. Please run the script again.")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()