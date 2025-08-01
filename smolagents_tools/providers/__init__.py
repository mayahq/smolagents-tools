"""
Provider modules for smolagents_tools

This package contains provider-specific implementations for various AI services.
"""

# Make BedrockClient available at package level for backward compatibility
try:
    from .bedrock import BedrockClient
    __all__ = ['BedrockClient']
except ImportError:
    # boto3 not available
    __all__ = []