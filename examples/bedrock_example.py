"""
AWS Bedrock Example with smolagents-tools

This example demonstrates how to use AWS Bedrock models with our ChatCompletionTool
and integrate them with smolagents CodeAgent for cross-region inference.
"""

import os
import sys
import asyncio

# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our tools
from smolagents_tools import ChatCompletionTool, create_ai_toolset

# Import smolagents components
try:
    from smolagents import CodeAgent, InferenceClientModel, tool
    SMOLAGENTS_AVAILABLE = True
    print("✅ Smolagents is available")
except ImportError:
    print("❌ Smolagents not installed. Install with: pip install smolagents")
    SMOLAGENTS_AVAILABLE = False

# Check for boto3
try:
    import boto3
    BOTO3_AVAILABLE = True
    print("✅ boto3 is available for Bedrock support")
except ImportError:
    print("❌ boto3 not installed. Install with: pip install boto3")
    BOTO3_AVAILABLE = False


# Popular Bedrock model IDs
BEDROCK_MODELS = {
    "claude-3.5-sonnet": "anthropic.claude-3-5-sonnet-20240620-v1:0",
    "claude-3.7-sonnet": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    "llama-3.1-8b": "meta.llama3-1-8b-instruct-v1:0",
    "llama-3.1-70b": "meta.llama3-1-70b-instruct-v1:0",
    "llama-3.1-405b": "meta.llama3-1-405b-instruct-v1:0",
}

# AWS regions with Bedrock support
BEDROCK_REGIONS = [
    "us-east-2",      # N. Virginia
]


async def test_bedrock_basic():
    """Test basic Bedrock functionality"""
    print("\n🔧 Testing Basic Bedrock Functionality")
    print("=" * 50)
    
    if not BOTO3_AVAILABLE:
        print("❌ boto3 not available. Skipping Bedrock tests.")
        return False
    
    try:
        # Test ChatCompletionTool with Bedrock
        chat_tool = ChatCompletionTool()
        
        # Simple test message
        result = await chat_tool.execute(
            messages="Hello! Please respond with a brief greeting.",
            provider="bedrock",
            model=BEDROCK_MODELS["claude-3.7-sonnet"],  # Use Claude 3.7 Sonnet
            region="us-east-2",
            max_tokens=100
        )
        
        if result.success:
            print("✅ Bedrock basic test successful!")
            print(f"Response: {result.artifacts['response']}")
            return True
        else:
            print(f"❌ Bedrock test failed: {result.error}")
            return False
            
    except Exception as e:
        print(f"❌ Bedrock test error: {e}")
        return False


async def test_bedrock_cross_region():
    """Test cross-region inference with different models"""
    print("\n🌍 Testing Cross-Region Inference")
    print("=" * 50)
    
    if not BOTO3_AVAILABLE:
        print("❌ boto3 not available. Skipping cross-region tests.")
        return
    
    # Test different regions (starting with us-east-2 where you have authorization)
    test_regions = ["us-east-2"]
    
    for region in test_regions:
        print(f"\n🔄 Testing region: {region}")
        try:
            chat_tool = ChatCompletionTool()
            
            result = await chat_tool.execute(
                messages=f"What region are you running in? Please respond briefly.",
                provider="bedrock",
                model=BEDROCK_MODELS["claude-3.7-sonnet"],
                region=region,
                max_tokens=50
            )
            
            if result.success:
                print(f"✅ {region}: {result.artifacts['response']}")
            else:
                print(f"❌ {region}: {result.error}")
                
        except Exception as e:
            print(f"❌ {region}: Error - {e}")


async def test_bedrock_models():
    """Test different Bedrock models"""
    print("\n🤖 Testing Different Bedrock Models")
    print("=" * 50)
    
    if not BOTO3_AVAILABLE:
        print("❌ boto3 not available. Skipping model tests.")
        return
    
    # Test the Claude 3.7 Sonnet model that we know works
    test_models = [
        ("Claude 3.7 Sonnet", BEDROCK_MODELS["claude-3.7-sonnet"]),
    ]
    
    for model_name, model_id in test_models:
        print(f"\n🔄 Testing {model_name}...")
        try:
            chat_tool = ChatCompletionTool()
            
            result = await chat_tool.execute(
                messages="Please say hello and mention your model name briefly.",
                provider="bedrock",
                model=model_id,
                region="us-east-1",
                max_tokens=100
            )
            
            if result.success:
                print(f"✅ {model_name}: {result.artifacts['response']}")
            else:
                print(f"❌ {model_name}: {result.error}")
                
        except Exception as e:
            print(f"❌ {model_name}: Error - {e}")


@tool
def bedrock_chat(prompt: str, model: str = "claude-3-haiku", region: str = "us-east-1") -> str:
    """
    Chat with AWS Bedrock models using cross-region inference.
    
    Args:
        prompt: The message to send to the model
        model: Model to use (claude-3-haiku, claude-3-sonnet, etc.)
        region: AWS region for inference
    
    Returns:
        The model's response
    """
    import asyncio
    from smolagents_tools import ChatCompletionTool
    
    # Map friendly names to full model IDs
    model_id = BEDROCK_MODELS.get(model, model)
    
    chat_tool = ChatCompletionTool()
    
    # Run async function in sync context
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, chat_tool.execute(
                    messages=prompt,
                    provider="bedrock",
                    model=model_id,
                    region=region,
                    max_tokens=500
                ))
                result = future.result()
        else:
            result = loop.run_until_complete(chat_tool.execute(
                messages=prompt,
                provider="bedrock",
                model=model_id,
                region=region,
                max_tokens=500
            ))
    except RuntimeError:
        result = asyncio.run(chat_tool.execute(
            messages=prompt,
            provider="bedrock",
            model=model_id,
            region=region,
            max_tokens=500
        ))
    
    if result.success:
        return result.artifacts["response"]
    else:
        return f"Error: {result.error}"


def test_bedrock_with_codeagent():
    """Test Bedrock integration with smolagents CodeAgent"""
    print("\n🤖 Testing Bedrock with CodeAgent")
    print("=" * 50)
    
    if not SMOLAGENTS_AVAILABLE:
        print("❌ Smolagents not available. Skipping CodeAgent test.")
        return
    
    if not BOTO3_AVAILABLE:
        print("❌ boto3 not available. Skipping CodeAgent test.")
        return
    
    try:
        # Note: For CodeAgent, we'd typically use a model that supports the smolagents interface
        # This is more of a demonstration of how the tools could work together
        
        # Create agent with Bedrock tool
        from smolagents import CodeAgent, InferenceClientModel
        
        # You would need to configure a model that works with smolagents
        # This is just showing how our Bedrock tool can be used
        tools = [bedrock_chat]
        
        print("✅ Bedrock tool created and ready for CodeAgent integration")
        print("💡 To use with CodeAgent, you would:")
        print("   1. Configure AWS credentials")
        print("   2. Set up a smolagents-compatible model")
        print("   3. Create CodeAgent with Bedrock tools")
        print("   4. Run tasks that leverage Bedrock models")
        
        # Example of how it would work:
        print("\n📝 Example usage:")
        print("agent = CodeAgent(tools=[bedrock_chat], model=your_model)")
        print("result = agent.run('Use Bedrock to analyze this data and provide insights')")
        
    except Exception as e:
        print(f"❌ CodeAgent integration error: {e}")


def show_bedrock_setup():
    """Show how to set up AWS Bedrock"""
    print("\n⚙️  AWS Bedrock Setup Guide")
    print("=" * 50)
    
    print("1. Install boto3:")
    print("   pip install boto3")
    
    print("\n2. Configure AWS credentials (choose one):")
    print("   a) AWS CLI: aws configure")
    print("   b) Environment variables:")
    print("      export AWS_ACCESS_KEY_ID=your_access_key")
    print("      export AWS_SECRET_ACCESS_KEY=your_secret_key")
    print("      export AWS_DEFAULT_REGION=us-east-2")
    print("   c) IAM roles (for EC2/Lambda)")
    print("   d) AWS credentials file (~/.aws/credentials)")
    
    print("\n3. Enable Bedrock models in AWS Console:")
    print("   - Go to AWS Bedrock console")
    print("   - Navigate to 'Model access'")
    print("   - Request access to desired models")
    print("   - Wait for approval (usually instant for most models)")
    
    print("\n4. Required IAM permissions:")
    print("   - bedrock:InvokeModel")
    print("   - bedrock:InvokeModelWithResponseStream")
    
    print(f"\n5. Available regions: {', '.join(BEDROCK_REGIONS)}")
    
    print(f"\n6. Popular models:")
    for name, model_id in BEDROCK_MODELS.items():
        print(f"   - {name}: {model_id}")


async def main():
    """Main function to run all tests"""
    print("🚀 AWS Bedrock Integration Demo")
    print("=" * 60)
    
    # Show setup guide
    show_bedrock_setup()
    
    # Check prerequisites
    if not BOTO3_AVAILABLE:
        print("\n❌ boto3 not installed. Please install it to use Bedrock features.")
        print("Install with: pip install boto3")
        return
    
    # Check AWS credentials
    try:
        import boto3
        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials is None:
            print("\n❌ AWS credentials not configured.")
            print("Please configure AWS credentials before running Bedrock tests.")
            return
        else:
            print(f"\n✅ AWS credentials configured for region: {session.region_name or 'default'}")
    except Exception as e:
        print(f"\n❌ AWS configuration error: {e}")
        return
    
    # Run tests
    print("\n" + "=" * 60)
    print("Running Bedrock Tests...")
    
    # Basic functionality test
    basic_success = await test_bedrock_basic()
    
    if basic_success:
        # Only run other tests if basic test passes
        await test_bedrock_cross_region()
        await test_bedrock_models()
    
    # Test CodeAgent integration
    test_bedrock_with_codeagent()
    
    print("\n" + "=" * 60)
    print("🎉 Bedrock demo completed!")
    print("\n💡 Next steps:")
    print("- Configure your preferred models and regions")
    print("- Integrate with smolagents CodeAgent")
    print("- Build AI applications with cross-region inference")


if __name__ == "__main__":
    asyncio.run(main())