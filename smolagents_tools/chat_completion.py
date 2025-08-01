"""
Chat completion tool adapted for smolagents with AWS Bedrock support
"""

import json
from typing import List, Dict, Any, Optional, Union
from .base import AsyncSmolTool, SmolToolResult

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from .providers.bedrock import BedrockClient
    BEDROCK_AVAILABLE = True
except ImportError:
    BEDROCK_AVAILABLE = False


class ChatCompletionTool(AsyncSmolTool):
    """
    A tool for generating chat completions using various LLM providers
    Adapted from OpenManus CreateChatCompletion with AWS Bedrock support
    """
    
    def __init__(self):
        self.name = "chat_completion"
        self.description = """Generate chat completions using various LLM providers (OpenAI, Anthropic, AWS Bedrock, local). Can handle conversations and single prompts."""
        
        self.inputs = {
            "messages": {
                "type": "string",
                "description": "JSON string of messages array or single message string",
                "required": True
            },
            "provider": {
                "type": "string",
                "description": "LLM provider: openai, anthropic, bedrock, local",
                "default": "openai",
                "required": False
            },
            "model": {
                "type": "string",
                "description": "Model name (e.g., gpt-4, claude-3-sonnet, anthropic.claude-3-sonnet-20240229-v1:0, etc.)",
                "default": "gpt-3.5-turbo",
                "required": False
            },
            "temperature": {
                "type": "number",
                "description": "Temperature for response generation (0.0 to 2.0)",
                "default": 0.7,
                "required": False
            },
            "max_tokens": {
                "type": "integer",
                "description": "Maximum tokens in response",
                "default": 1000,
                "required": False
            },
            "system_prompt": {
                "type": "string",
                "description": "System prompt to set context",
                "required": False
            },
            "api_key": {
                "type": "string",
                "description": "API key for the provider (if not set in environment)",
                "required": False
            },
            "base_url": {
                "type": "string",
                "description": "Base URL for API (for local or custom endpoints)",
                "required": False
            },
            "region": {
                "type": "string",
                "description": "AWS region for Bedrock (default: us-east-1)",
                "default": "us-east-1",
                "required": False
            },
            "stream": {
                "type": "boolean",
                "description": "Enable streaming response",
                "default": False,
                "required": False
            }
        }
        self.output_type = "string"
        super().__init__()
    
    def _parse_messages(self, messages: Union[str, List[Dict[str, str]]]) -> List[Dict[str, str]]:
        """Parse messages input into proper format"""
        if isinstance(messages, str):
            try:
                # Try to parse as JSON first
                parsed = json.loads(messages)
                if isinstance(parsed, list):
                    return parsed
                elif isinstance(parsed, dict):
                    return [parsed]
                else:
                    # Treat as simple string message
                    return [{"role": "user", "content": messages}]
            except json.JSONDecodeError:
                # Treat as simple string message
                return [{"role": "user", "content": messages}]
        elif isinstance(messages, list):
            return messages
        else:
            return [{"role": "user", "content": str(messages)}]
    
    def _add_system_prompt(self, messages: List[Dict[str, str]], system_prompt: str) -> List[Dict[str, str]]:
        """Add system prompt to messages"""
        if system_prompt:
            # Check if first message is already a system message
            if messages and messages[0].get("role") == "system":
                messages[0]["content"] = system_prompt + "\n\n" + messages[0]["content"]
            else:
                messages.insert(0, {"role": "system", "content": system_prompt})
        return messages
    
    async def _openai_completion(self, messages: List[Dict[str, str]], model: str, 
                                temperature: float, max_tokens: int, api_key: str = None,
                                base_url: str = None) -> SmolToolResult:
        """Generate completion using OpenAI API"""
        if not OPENAI_AVAILABLE:
            return SmolToolResult(
                error="OpenAI library not available. Install with: pip install openai",
                success=False
            )
        
        try:
            client_kwargs = {}
            if api_key:
                client_kwargs["api_key"] = api_key
            if base_url:
                client_kwargs["base_url"] = base_url
            
            client = openai.AsyncOpenAI(**client_kwargs)
            
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            usage = response.usage
            
            result_text = f"Response: {content}\n\n"
            result_text += f"Usage: {usage.prompt_tokens} prompt tokens, {usage.completion_tokens} completion tokens, {usage.total_tokens} total tokens"
            
            return SmolToolResult(
                output=result_text,
                success=True,
                artifacts={
                    "response": content,
                    "usage": usage.model_dump() if hasattr(usage, 'model_dump') else dict(usage),
                    "model": model
                }
            )
            
        except Exception as e:
            return SmolToolResult(
                error=f"OpenAI API error: {str(e)}",
                success=False
            )
    
    async def _anthropic_completion(self, messages: List[Dict[str, str]], model: str,
                                   temperature: float, max_tokens: int, api_key: str = None) -> SmolToolResult:
        """Generate completion using Anthropic API"""
        if not ANTHROPIC_AVAILABLE:
            return SmolToolResult(
                error="Anthropic library not available. Install with: pip install anthropic",
                success=False
            )
        
        try:
            client_kwargs = {}
            if api_key:
                client_kwargs["api_key"] = api_key
            
            client = anthropic.AsyncAnthropic(**client_kwargs)
            
            # Convert messages format for Anthropic
            system_message = None
            anthropic_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    anthropic_messages.append(msg)
            
            kwargs = {
                "model": model,
                "messages": anthropic_messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            if system_message:
                kwargs["system"] = system_message
            
            response = await client.messages.create(**kwargs)
            
            content = response.content[0].text
            usage = response.usage
            
            result_text = f"Response: {content}\n\n"
            result_text += f"Usage: {usage.input_tokens} input tokens, {usage.output_tokens} output tokens"
            
            return SmolToolResult(
                output=result_text,
                success=True,
                artifacts={
                    "response": content,
                    "usage": {
                        "input_tokens": usage.input_tokens,
                        "output_tokens": usage.output_tokens,
                        "total_tokens": usage.input_tokens + usage.output_tokens
                    },
                    "model": model
                }
            )
            
        except Exception as e:
            return SmolToolResult(
                error=f"Anthropic API error: {str(e)}",
                success=False
            )
    
    async def _bedrock_completion(self, messages: List[Dict[str, str]], model: str,
                                 temperature: float, max_tokens: int, region: str = "us-east-1",
                                 stream: bool = False) -> SmolToolResult:
        """Generate completion using AWS Bedrock with cross-region inference"""
        if not BEDROCK_AVAILABLE:
            return SmolToolResult(
                error="Bedrock client not available. Install boto3 with: pip install boto3",
                success=False
            )
        
        try:
            # Initialize Bedrock client with specified region and bedrock profile
            bedrock_client = BedrockClient(region_name=region, profile_name="bedrock")
            
            # Use the chat completions interface
            response = await bedrock_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            # Extract response content
            content = response.choices[0].message.content
            usage = response.usage
            
            result_text = f"Response: {content}\n\n"
            result_text += f"Model: {model} (AWS Bedrock)\n"
            result_text += f"Region: {region}\n"
            result_text += f"Usage: {usage.prompt_tokens} prompt tokens, {usage.completion_tokens} completion tokens, {usage.total_tokens} total tokens"
            
            return SmolToolResult(
                output=result_text,
                success=True,
                artifacts={
                    "response": content,
                    "usage": {
                        "prompt_tokens": usage.prompt_tokens,
                        "completion_tokens": usage.completion_tokens,
                        "total_tokens": usage.total_tokens
                    },
                    "model": model,
                    "provider": "bedrock",
                    "region": region
                }
            )
            
        except Exception as e:
            return SmolToolResult(
                error=f"AWS Bedrock error: {str(e)}",
                success=False
            )
    
    async def _local_completion(self, messages: List[Dict[str, str]], model: str,
                               temperature: float, max_tokens: int, base_url: str = None) -> SmolToolResult:
        """Generate completion using local API (e.g., Ollama, local OpenAI-compatible server)"""
        try:
            import aiohttp
            
            if not base_url:
                base_url = "http://localhost:11434"  # Default Ollama URL
            
            # Format for Ollama API
            if "ollama" in base_url or ":11434" in base_url:
                # Ollama format
                prompt = ""
                for msg in messages:
                    if msg["role"] == "system":
                        prompt += f"System: {msg['content']}\n"
                    elif msg["role"] == "user":
                        prompt += f"User: {msg['content']}\n"
                    elif msg["role"] == "assistant":
                        prompt += f"Assistant: {msg['content']}\n"
                
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(f"{base_url}/api/generate", json=payload) as response:
                        if response.status == 200:
                            result = await response.json()
                            content = result.get("response", "")
                            
                            return SmolToolResult(
                                output=f"Response: {content}",
                                success=True,
                                artifacts={
                                    "response": content,
                                    "model": model
                                }
                            )
                        else:
                            error_text = await response.text()
                            return SmolToolResult(
                                error=f"Local API error: {response.status} - {error_text}",
                                success=False
                            )
            else:
                # OpenAI-compatible format
                payload = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(f"{base_url}/v1/chat/completions", json=payload) as response:
                        if response.status == 200:
                            result = await response.json()
                            content = result["choices"][0]["message"]["content"]
                            usage = result.get("usage", {})
                            
                            result_text = f"Response: {content}"
                            if usage:
                                result_text += f"\n\nUsage: {usage.get('prompt_tokens', 0)} prompt tokens, {usage.get('completion_tokens', 0)} completion tokens"
                            
                            return SmolToolResult(
                                output=result_text,
                                success=True,
                                artifacts={
                                    "response": content,
                                    "usage": usage,
                                    "model": model
                                }
                            )
                        else:
                            error_text = await response.text()
                            return SmolToolResult(
                                error=f"Local API error: {response.status} - {error_text}",
                                success=False
                            )
                            
        except Exception as e:
            return SmolToolResult(
                error=f"Local completion error: {str(e)}",
                success=False
            )
    
    async def execute(self, messages: Union[str, List[Dict[str, str]]], 
                     provider: str = "openai", model: str = "gpt-3.5-turbo",
                     temperature: float = 0.7, max_tokens: int = 1000,
                     system_prompt: str = None, api_key: str = None,
                     base_url: str = None, region: str = "us-east-1",
                     stream: bool = False, **kwargs) -> SmolToolResult:
        """
        Generate chat completion.
        
        Args:
            messages: Messages for completion (JSON string or list)
            provider: LLM provider to use (openai, anthropic, bedrock, local)
            model: Model name
            temperature: Response temperature
            max_tokens: Maximum response tokens
            system_prompt: System prompt for context
            api_key: API key for provider
            base_url: Base URL for local/custom APIs
            region: AWS region for Bedrock
            stream: Enable streaming response
            
        Returns:
            SmolToolResult: Generated completion
        """
        try:
            # Parse and format messages
            parsed_messages = self._parse_messages(messages)
            
            # Add system prompt if provided
            if system_prompt:
                parsed_messages = self._add_system_prompt(parsed_messages, system_prompt)
            
            # Validate messages format
            for msg in parsed_messages:
                if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                    return SmolToolResult(
                        error=f"Invalid message format: {msg}",
                        success=False
                    )
            
            # Route to appropriate provider
            if provider.lower() == "openai":
                return await self._openai_completion(
                    parsed_messages, model, temperature, max_tokens, api_key, base_url
                )
            elif provider.lower() == "anthropic":
                return await self._anthropic_completion(
                    parsed_messages, model, temperature, max_tokens, api_key
                )
            elif provider.lower() == "bedrock":
                return await self._bedrock_completion(
                    parsed_messages, model, temperature, max_tokens, region, stream
                )
            elif provider.lower() == "local":
                return await self._local_completion(
                    parsed_messages, model, temperature, max_tokens, base_url
                )
            else:
                return SmolToolResult(
                    error=f"Unknown provider: {provider}. Supported: openai, anthropic, bedrock, local",
                    success=False
                )
                
        except Exception as e:
            return SmolToolResult(
                error=f"Chat completion error: {str(e)}",
                success=False
            )


class SimplePromptTool(AsyncSmolTool):
    """Simple tool for single prompt completions"""
    
    def __init__(self):
        self.name = "simple_prompt"
        self.description = "Generate a simple completion from a single prompt"
        
        self.inputs = {
            "prompt": {
                "type": "string",
                "description": "The prompt to complete",
                "required": True
            },
            "provider": {
                "type": "string",
                "description": "Provider to use: openai, anthropic, bedrock, local",
                "default": "openai",
                "required": False
            },
            "model": {
                "type": "string",
                "description": "Model to use",
                "default": "gpt-3.5-turbo",
                "required": False
            },
            "max_tokens": {
                "type": "integer",
                "description": "Maximum tokens in response",
                "default": 500,
                "required": False
            }
        }
        self.output_type = "string"
        super().__init__()
    
    async def execute(self, prompt: str, provider: str = "openai", 
                     model: str = "gpt-3.5-turbo", max_tokens: int = 500, 
                     **kwargs) -> SmolToolResult:
        """Generate simple completion"""
        try:
            # Use the main chat completion tool
            chat_tool = ChatCompletionTool()
            
            result = await chat_tool.execute(
                messages=prompt,
                provider=provider,
                model=model,
                max_tokens=max_tokens,
                temperature=0.7,
                **kwargs
            )
            
            if result.success and result.artifacts:
                # Extract just the response content
                response = result.artifacts.get("response", result.output)
                return SmolToolResult(
                    output=response,
                    success=True
                )
            else:
                return result
                
        except Exception as e:
            return SmolToolResult(
                error=f"Simple prompt error: {str(e)}",
                success=False
            )