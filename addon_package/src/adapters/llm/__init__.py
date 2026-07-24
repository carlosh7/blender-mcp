"""
blender-mcp-ultra — LLM Adapter Base
Base class and implementations for LLM providers.
"""
import json
import os
import time
import urllib.request
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from core.interfaces import ILLMProvider


@dataclass
class LLMConfig:
    """Configuration for LLM provider."""
    api_key: str
    api_url: str
    model: str
    timeout: int = 60
    max_tokens: int = 8192
    temperature: float = 0.4


class BaseLLMProvider(ILLMProvider):
    """
    Base class for LLM providers.
    Implements common functionality.
    """
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._validated = False
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat messages and get response."""
        raise NotImplementedError("Subclasses must implement chat()")
    
    def validate_api_key(self) -> bool:
        """Validate API key."""
        if not self.config.api_key:
            return False
        
        try:
            headers = self._get_headers()
            headers['Authorization'] = f'Bearer {self.config.api_key}'
            
            req = urllib.request.Request(
                self.config.api_url,
                headers=headers,
                method='GET'
            )
            urllib.request.urlopen(req, timeout=10)
            self._validated = True
            return True
        except Exception:
            return False
    
    def get_models(self) -> List[str]:
        """Get available models."""
        return []
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return self.__class__.__name__
    
    @abstractmethod
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API calls."""
        pass
    
    @abstractmethod
    def _build_request_body(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Build request body for API call."""
        pass
    
    @abstractmethod
    def _parse_response(self, response: Dict[str, Any]) -> str:
        """Parse API response to extract text."""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider."""
    
    def __init__(self, config: LLMConfig):
        config.api_url = config.api_url or "https://api.openai.com/v1/chat/completions"
        super().__init__(config)
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat messages and get response."""
        body = self._build_request_body(messages, **kwargs)
        
        req = urllib.request.Request(
            self.config.api_url,
            data=json.dumps(body).encode(),
            headers=self._get_headers(),
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=self.config.timeout) as resp:
            response = json.loads(resp.read())
            return self._parse_response(response)
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.config.api_key}',
        }
    
    def _build_request_body(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        return {
            'model': self.config.model,
            'messages': messages,
            'max_tokens': kwargs.get('max_tokens', self.config.max_tokens),
            'temperature': kwargs.get('temperature', self.config.temperature),
        }
    
    def _parse_response(self, response: Dict[str, Any]) -> str:
        return response.get('choices', [{}])[0].get('message', {}).get('content', '')
    
    def get_models(self) -> List[str]:
        """Get available OpenAI models."""
        return [
            'gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo',
            'gpt-3.5-turbo', 'o1', 'o1-mini',
        ]


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude API provider."""
    
    def __init__(self, config: LLMConfig):
        config.api_url = config.api_url or "https://api.anthropic.com/v1/messages"
        super().__init__(config)
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat messages and get response."""
        body = self._build_request_body(messages, **kwargs)
        
        req = urllib.request.Request(
            self.config.api_url,
            data=json.dumps(body).encode(),
            headers=self._get_headers(),
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=self.config.timeout) as resp:
            response = json.loads(resp.read())
            return self._parse_response(response)
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            'Content-Type': 'application/json',
            'x-api-key': self.config.api_key,
            'anthropic-version': '2023-06-01',
        }
    
    def _build_request_body(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        # Separate system from user/assistant messages
        system = ""
        chat_messages = []
        
        for msg in messages:
            if msg['role'] == 'system':
                system += msg['content'] + '\n'
            else:
                chat_messages.append(msg)
        
        return {
            'model': self.config.model,
            'max_tokens': kwargs.get('max_tokens', self.config.max_tokens),
            'system': system.strip(),
            'messages': chat_messages,
            'temperature': kwargs.get('temperature', self.config.temperature),
        }
    
    def _parse_response(self, response: Dict[str, Any]) -> str:
        content = ""
        for block in response.get('content', []):
            if block.get('type') == 'text':
                content += block.get('text', '')
        return content
    
    def get_models(self) -> List[str]:
        """Get available Anthropic models."""
        return [
            'claude-sonnet-4-20250514', 'claude-3-5-haiku-20241022',
            'claude-3-opus-20240229',
        ]


class GoogleProvider(BaseLLMProvider):
    """Google Gemini API provider."""
    
    def __init__(self, config: LLMConfig):
        config.api_url = config.api_url or f"https://generativelanguage.googleapis.com/v1beta/models/{config.model}:generateContent"
        super().__init__(config)
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat messages and get response."""
        body = self._build_request_body(messages, **kwargs)
        
        url = f"{self.config.api_url}?key={self.config.api_key}"
        
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode(),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=self.config.timeout) as resp:
            response = json.loads(resp.read())
            return self._parse_response(response)
    
    def _get_headers(self) -> Dict[str, str]:
        return {'Content-Type': 'application/json'}
    
    def _build_request_body(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        contents = []
        for msg in messages:
            if msg['role'] != 'system':
                contents.append({
                    'parts': [{'text': msg['content']}]
                })
        
        return {
            'contents': contents,
            'generationConfig': {
                'maxOutputTokens': kwargs.get('max_tokens', self.config.max_tokens),
                'temperature': kwargs.get('temperature', self.config.temperature),
            }
        }
    
    def _parse_response(self, response: Dict[str, Any]) -> str:
        candidates = response.get('candidates', [])
        if candidates:
            return candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        return ''
    
    def get_models(self) -> List[str]:
        """Get available Google models."""
        return ['gemini-2.0-flash', 'gemini-1.5-pro', 'gemini-1.5-flash']


class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek API provider."""
    
    def __init__(self, config: LLMConfig):
        config.api_url = config.api_url or "https://api.deepseek.com/v1/chat/completions"
        super().__init__(config)
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat messages and get response."""
        body = self._build_request_body(messages, **kwargs)
        
        req = urllib.request.Request(
            self.config.api_url,
            data=json.dumps(body).encode(),
            headers=self._get_headers(),
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=self.config.timeout) as resp:
            response = json.loads(resp.read())
            return self._parse_response(response)
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.config.api_key}',
        }
    
    def _build_request_body(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        return {
            'model': self.config.model,
            'messages': messages,
            'max_tokens': kwargs.get('max_tokens', self.config.max_tokens),
            'temperature': kwargs.get('temperature', self.config.temperature),
        }
    
    def _parse_response(self, response: Dict[str, Any]) -> str:
        return response.get('choices', [{}])[0].get('message', {}).get('content', '')
    
    def get_models(self) -> List[str]:
        """Get available DeepSeek models."""
        return ['deepseek-chat', 'deepseek-coder', 'deepseek-reasoner']


def create_provider(provider_name: str, config: LLMConfig) -> ILLMProvider:
    """
    Factory function to create LLM provider.
    
    Args:
        provider_name: Name of the provider
        config: Provider configuration
        
    Returns:
        LLM provider instance
    """
    providers = {
        'openai': OpenAIProvider,
        'anthropic': AnthropicProvider,
        'google': GoogleProvider,
        'deepseek': DeepSeekProvider,
    }
    
    provider_class = providers.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider_name}")
    
    return provider_class(config)
