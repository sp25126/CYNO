"""
Cloud GPU Infrastructure for Cyno Job Agent

This module provides cloud-based resume parsing using free Google Colab GPU resources
with automatic fallback to local Ollama for resilience.

Components:
- colab_server.py: FastAPI server for Colab deployment
- cloud_client.py: Local client with smart fallback logic

Usage:
    # Option 1: Use environment variable
    export COLAB_SERVER_URL="https://your-ngrok-url.ngrok.io"
    
    from cloud.cloud_client import parse_resume
    result = parse_resume(resume_text)
    
    # Option 2: Direct configuration
    from cloud.cloud_client import CloudClient
    client = CloudClient(server_url="https://your-ngrok-url.ngrok.io")
    result = client.parse_resume(resume_text)
"""

from .cloud_client import CloudClient, get_client, parse_resume

__all__ = ['CloudClient', 'get_client', 'parse_resume']
