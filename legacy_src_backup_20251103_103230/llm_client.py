"""
Backward compatibility layer for legacy llm_client imports.

DEPRECATED: This module is maintained for backward compatibility only.
New code should import from the 'llm' package instead:

    from llm import (
        create_llm_client,
        LLMResponse,
        LLMClient,
        OpenAIClient,
        AnthropicClient,
        BedrockClient,
        LLaMAClient,
    )

The modular llm package provides better organization, error handling,
and follows SOLID principles. See docs/REFACTORING_PHASE2_REPORT.md for details.
"""

import warnings
import os
import logging
from typing import Optional, List, Dict, Any, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass

# Issue deprecation warning
warnings.warn(
    "Importing from llm_client is deprecated and will be removed in a future version. "
    "Use 'from llm import ...' instead. "
    "See docs/REFACTORING_PHASE2_REPORT.md for migration guide.",
    DeprecationWarning,
    stacklevel=2
)

def _import_requests():
    try:
        import requests
        return requests
    except ImportError:
        raise ImportError("requests library is required for LLaMA client. Install with: pip install requests")

def _import_boto3():
    try:
        import boto3
        from botocore.exceptions import ClientError
        return boto3, ClientError
    except ImportError:
        raise ImportError("boto3 is required for AWS Bedrock client. Install with: pip install boto3")

def _import_langchain():
    try:
        from langchain_openai import ChatOpenAI
        from langchain.schema import HumanMessage, SystemMessage, BaseMessage
        return ChatOpenAI, HumanMessage, SystemMessage, BaseMessage
    except ImportError:
        raise ImportError("langchain libraries are required. Install with: pip install langchain langchain-openai")

def _import_anthropic():
    try:
        import anthropic
        return anthropic
    except ImportError:
        raise ImportError("anthropic library is required for Claude client. Install with: pip install anthropic")

def _import_json():
    import json
    return json

logger = logging.getLogger(__name__)

__all__ = [
    'LLMResponse',
    'LLMClient', 
    'OpenAIClient',
    'AnthropicClient',
    'BedrockClient',
    'LLaMAClient',  
    'LLMClientFactory',
    'create_llm_client'
]


@dataclass
class LLMResponse:
    """Standardized response format for both OpenAI and LLaMA."""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    def generate(self, messages: List[Any], **kwargs) -> LLMResponse:
        """Generate response from messages."""
        pass
    
    @abstractmethod
    def generate_text(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate response from text prompt."""
        pass


class AnthropicClient(LLMClient):
    """Anthropic Claude API client with comprehensive error handling and rate limiting."""
    
    def __init__(
        self,
        model: str = "claude-3-haiku-20240307",
        api_key: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
        max_retries: int = 3,
        **kwargs
    ):
        """
        Initialize Anthropic client.
        
        Args:
            model: Claude model name (claude-3-haiku, claude-3-sonnet, claude-3-opus, claude-3.5-sonnet)
            api_key: Anthropic API key
            temperature: Generation temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for rate limiting
            **kwargs: Additional Anthropic client parameters
        """
        anthropic = _import_anthropic()
        
        self.model = model
        self.max_retries = max_retries
        self.timeout = timeout or 60
        self.temperature = temperature
        
        valid_models = [
            "claude-3-haiku-20240307", "claude-3-sonnet-20240229", "claude-3-opus-20240229",
            "claude-3-5-sonnet-20240620", "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"
        ]
        if model not in valid_models:
            logger.warning(f"Model '{model}' not in known valid models. Proceeding anyway.")
        
        if max_tokens is None:
            if "opus" in model.lower():
                max_tokens = 4000
            elif "sonnet" in model.lower():
                max_tokens = 2000
            else: 
                max_tokens = 1000
        
        self.max_tokens = max_tokens
        
        try:
            api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            
            if not api_key:
                raise ValueError(
                    "Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable "
                    "or pass api_key parameter. Get your key from: https://console.anthropic.com/"
                )
            
            self.client = anthropic.Anthropic(
                api_key=api_key,
                timeout=self.timeout,
                max_retries=self.max_retries,
                **kwargs
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            raise ValueError(f"Anthropic client initialization failed: {e}")
        
        logger.info(f"Initialized Anthropic client with model: {model} (max_tokens: {max_tokens})")
    
    def _format_messages_for_anthropic(self, messages: List[Any]) -> tuple[str, List[Dict[str, str]]]:
        """
        Format LangChain messages for Anthropic Claude API.
        
        Returns:
            Tuple of (system_message, formatted_messages)
        """
        _, HumanMessage, SystemMessage, _ = _import_langchain()
        
        system_message = ""
        formatted_messages = []
        
        for message in messages:
            if isinstance(message, SystemMessage):
                system_message = message.content
            elif isinstance(message, HumanMessage):
                formatted_messages.append({
                    "role": "user",
                    "content": message.content
                })
            else:
                content = str(message.content) if hasattr(message, 'content') else str(message)
                formatted_messages.append({
                    "role": "user",
                    "content": content
                })
        
        if not formatted_messages and messages:
            content = " ".join(str(msg) for msg in messages)
            formatted_messages.append({
                "role": "user",
                "content": content
            })
        
        return system_message, formatted_messages
    
    def generate(self, messages: List[Any], **kwargs) -> LLMResponse:
        """Generate response using Anthropic Claude API with comprehensive error handling."""
        import time
        from random import uniform
        
        for attempt in range(self.max_retries + 1):
            try:
                system_message, formatted_messages = self._format_messages_for_anthropic(messages)
                
                api_params = {
                    "model": self.model,
                    "messages": formatted_messages,
                    "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                    "temperature": kwargs.get("temperature", self.temperature),
                }
                
                if system_message:
                    api_params["system"] = system_message
                
                if self.timeout:
                    api_params["timeout"] = self.timeout
                
                response = self.client.messages.create(**api_params)
                
                content = ""
                if response.content and len(response.content) > 0:
                    content_blocks = []
                    for block in response.content:
                        if hasattr(block, 'text'):
                            content_blocks.append(block.text)
                        elif hasattr(block, 'content'):
                            content_blocks.append(str(block.content))
                        else:
                            content_blocks.append(str(block))
                    content = "".join(content_blocks)
                
                usage = {}
                if hasattr(response, 'usage'):
                    usage = {
                        "prompt_tokens": getattr(response.usage, 'input_tokens', 0),
                        "completion_tokens": getattr(response.usage, 'output_tokens', 0),
                        "total_tokens": getattr(response.usage, 'input_tokens', 0) + getattr(response.usage, 'output_tokens', 0)
                    }
                
                return LLMResponse(
                    content=content,
                    model=self.model,
                    usage=usage,
                    finish_reason=getattr(response, 'stop_reason', 'stop'),
                    metadata={
                        "provider": "anthropic",
                        "attempt": attempt + 1,
                        "response_id": getattr(response, 'id', None),
                        "response_type": getattr(response, 'type', None)
                    }
                )
                
            except Exception as e:
                error_msg = str(e).lower()
                
                if "rate_limit_error" in error_msg or "429" in error_msg:
                    if attempt < self.max_retries:
                        wait_time = (2 ** attempt) + uniform(0, 1)
                        logger.warning(f"Rate limit hit, retrying in {wait_time:.1f}s (attempt {attempt + 1}/{self.max_retries + 1})")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error("Rate limit exceeded, max retries reached")
                        raise Exception(f"Anthropic rate limit exceeded after {self.max_retries} retries: {e}")
                
                elif "invalid_request_error" in error_msg or "authentication_error" in error_msg:
                    raise ValueError(
                        "Invalid Anthropic API key or request. Check your ANTHROPIC_API_KEY environment variable. "
                        "Get a valid key from: https://console.anthropic.com/"
                    )
                
                elif "not_found_error" in error_msg or "model" in error_msg and "not" in error_msg:
                    raise ValueError(f"Model '{self.model}' not available. Check model name and your API access.")
                
                elif "overloaded_error" in error_msg or "internal_server_error" in error_msg:
                    if attempt < self.max_retries:
                        wait_time = (2 ** attempt) + uniform(0, 1)
                        logger.warning(f"Server overloaded, retrying in {wait_time:.1f}s (attempt {attempt + 1}/{self.max_retries + 1})")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(f"Anthropic server overloaded after {self.max_retries} retries: {e}")
                
                elif "timeout" in error_msg:
                    if attempt < self.max_retries:
                        wait_time = 2 ** attempt
                        logger.warning(f"Request timeout, retrying in {wait_time}s (attempt {attempt + 1}/{self.max_retries + 1})")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(f"Anthropic request timeout after {self.max_retries} retries: {e}")
                
                else:
                    logger.error(f"Anthropic API error (attempt {attempt + 1}): {e}")
                    if attempt < self.max_retries:
                        wait_time = 2 ** attempt
                        logger.warning(f"Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(f"Anthropic API error after {self.max_retries} retries: {e}")
        
        raise Exception("Unexpected error in Anthropic client retry loop")
    
    def generate_text(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate response from text prompt."""
        _, HumanMessage, _, _ = _import_langchain()
        messages = [HumanMessage(content=prompt)]
        return self.generate(messages, **kwargs)


class OpenAIClient(LLMClient):
    """OpenAI API client using LangChain with comprehensive error handling and rate limiting."""
    
    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        api_key: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
        max_retries: int = 3,
        **kwargs
    ):
        """
        Initialize OpenAI client.
        
        Args:
            model: OpenAI model name (gpt-3.5-turbo, gpt-4, gpt-4-turbo)
            api_key: OpenAI API key
            temperature: Generation temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for rate limiting
            **kwargs: Additional ChatOpenAI parameters
        """
        ChatOpenAI, _, _, _ = _import_langchain()
        
        self.model = model
        self.max_retries = max_retries
        self.timeout = timeout or 60
        
        valid_models = [
            "gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-1106", "gpt-3.5-turbo-0125",
            "gpt-4", "gpt-4-32k", "gpt-4-1106-preview", "gpt-4-0125-preview", 
            "gpt-4-turbo", "gpt-4-turbo-preview", "gpt-4o", "gpt-4o-mini"
        ]
        if model not in valid_models:
            logger.warning(f"Model '{model}' not in known valid models. Proceeding anyway.")
        
        if max_tokens is None:
            if "32k" in model or "turbo" in model:
                max_tokens = 4000
            elif "gpt-4" in model:
                max_tokens = 2000
            else:
                max_tokens = 1000
        
        try:
            self.client = ChatOpenAI(
                model=model,
                openai_api_key=api_key or os.getenv("OPENAI_API_KEY"),
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=self.timeout,
                max_retries=self.max_retries,
                **kwargs
            )
            
            if not (api_key or os.getenv("OPENAI_API_KEY")):
                raise ValueError(
                    "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                    "or pass api_key parameter. Get your key from: https://platform.openai.com/api-keys"
                )
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise ValueError(f"OpenAI client initialization failed: {e}")
        
        logger.info(f"Initialized OpenAI client with model: {model} (max_tokens: {max_tokens})")
    
    def generate(self, messages: List[Any], **kwargs) -> LLMResponse:
        """Generate response using ChatOpenAI with comprehensive error handling."""
        import time
        from random import uniform
        
        for attempt in range(self.max_retries + 1):
            try:
                if 'timeout' not in kwargs:
                    kwargs['timeout'] = self.timeout
                
                response = self.client.invoke(messages, **kwargs)
                
                response_metadata = getattr(response, 'response_metadata', {})
                token_usage = response_metadata.get('token_usage', {})
                
                if token_usage and not isinstance(token_usage, dict):
                    token_usage = {}
                
                return LLMResponse(
                    content=response.content,
                    model=self.model,
                    usage=token_usage,
                    finish_reason=response_metadata.get('finish_reason', 'stop'),
                    metadata={
                        "provider": "openai",
                        "attempt": attempt + 1,
                        "response_metadata": response_metadata
                    }
                )
                
            except Exception as e:
                error_msg = str(e).lower()
                
                if "rate limit" in error_msg or "429" in error_msg:
                    if attempt < self.max_retries:
                        wait_time = (2 ** attempt) + uniform(0, 1)
                        logger.warning(f"Rate limit hit, retrying in {wait_time:.1f}s (attempt {attempt + 1}/{self.max_retries + 1})")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error("Rate limit exceeded, max retries reached")
                        raise Exception(f"OpenAI rate limit exceeded after {self.max_retries} retries: {e}")
                
                elif "invalid api key" in error_msg or "unauthorized" in error_msg:
                    raise ValueError(
                        "Invalid OpenAI API key. Check your OPENAI_API_KEY environment variable. "
                        "Get a valid key from: https://platform.openai.com/api-keys"
                    )
                
                elif "model not found" in error_msg or "does not exist" in error_msg:
                    raise ValueError(f"Model '{self.model}' not available. Check model name and your API access.")
                
                elif "context length" in error_msg or "maximum context" in error_msg:
                    raise ValueError(
                        f"Input too long for model '{self.model}'. "
                        "Try reducing input size or using a model with larger context window."
                    )
                
                elif "timeout" in error_msg:
                    if attempt < self.max_retries:
                        wait_time = 2 ** attempt
                        logger.warning(f"Request timeout, retrying in {wait_time}s (attempt {attempt + 1}/{self.max_retries + 1})")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(f"OpenAI request timeout after {self.max_retries} retries: {e}")
                
                else:
                    logger.error(f"OpenAI API error (attempt {attempt + 1}): {e}")
                    if attempt < self.max_retries:
                        wait_time = 2 ** attempt
                        logger.warning(f"Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(f"OpenAI API error after {self.max_retries} retries: {e}")
        
        raise Exception("Unexpected error in OpenAI client retry loop")
    
    def generate_text(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate response from text prompt."""
        _, HumanMessage, _, _ = _import_langchain()
        messages = [HumanMessage(content=prompt)]
        return self.generate(messages, **kwargs)


class BedrockClient(LLMClient):
    """AWS Bedrock client for LLaMA models using boto3."""
    
    def __init__(
        self,
        model: str = "meta.llama3-8b-instruct-v1:0",
        region_name: Optional[str] = None,
        aws_profile: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 2048,
        **kwargs
    ):
        """
        Initialize AWS Bedrock client.
        
        Args:
            model: Bedrock model ID (e.g., meta.llama3-8b-instruct-v1:0)
            region_name: AWS region for Bedrock service
            aws_profile: AWS profile to use (optional)
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
        """
        boto3, ClientError = _import_boto3()
        json = _import_json()
        
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.ClientError = ClientError
        self.json = json
        
        self.region = region_name or os.getenv("AWS_REGION", "us-east-1")
        
        try:
            if aws_profile:
                session = boto3.Session(profile_name=aws_profile)
                self.client = session.client("bedrock-runtime", region_name=self.region)
            else:
                self.client = boto3.client("bedrock-runtime", region_name=self.region)
                
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise ValueError(
                "Failed to initialize AWS Bedrock client. "
                "Ensure AWS credentials are configured via 'aws configure' or IAM roles."
            )
        
        logger.info(f"Initialized Bedrock client with model: {model} in region: {self.region}")
    
    def _format_messages_for_bedrock(self, messages: List[Any]) -> str:
        """
        Format LangChain messages for Bedrock LLaMA models.
        
        Bedrock LLaMA models expect specific chat format with instruction tags.
        """
        _, HumanMessage, SystemMessage, _ = _import_langchain()
        formatted_parts = []
        
        system_message = None
        user_messages = []
        
        for message in messages:
            if isinstance(message, SystemMessage):
                system_message = message.content
            elif isinstance(message, HumanMessage):
                user_messages.append(message.content)
            else:
                user_messages.append(str(message.content) if hasattr(message, 'content') else str(message))
        
        user_content = " ".join(user_messages)
        
        if system_message:
            formatted_prompt = (
                f"<s>[INST] <<SYS>>\n{system_message}\n<</SYS>>\n\n"
                f"{user_content} [/INST]"
            )
        else:
            formatted_prompt = f"<s>[INST] {user_content} [/INST]"
        
        return formatted_prompt
    
    def generate(self, messages: List[Any], **kwargs) -> LLMResponse:
        """Generate response using AWS Bedrock."""
        try:
            prompt = self._format_messages_for_bedrock(messages)
            
            request_body = {
                "prompt": prompt,
                "max_gen_len": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "top_p": kwargs.get("top_p", 0.9),
            }
            
            response = self.client.invoke_model(
                modelId=self.model,
                body=self.json.dumps(request_body),
                accept="application/json",
                contentType="application/json"
            )
            
            response_body = self.json.loads(response["body"].read())
            
            if "generation" not in response_body:
                raise ValueError("No generation found in Bedrock response")
            
            content = response_body["generation"].strip()
            
            if content.startswith("### Response:"):
                content = content.replace("### Response:", "").strip()
            
            import re
            
            lines = content.split('\n')
            clean_lines = []
            
            for line in lines:
                line = line.strip()
                if (line.startswith('Rank these products for the query') or 
                    line.startswith('Here are some products for:') or
                    'in order of preference:' in line):
                    continue
                if line and not line.startswith('[') and not line.startswith('<'):
                    clean_lines.append(line)
            
            if clean_lines:
                content = '\n'.join(clean_lines)
            
            content = re.sub(r'\[/?INST\]', '', content)
            content = re.sub(r'\[/?s\]', '', content)
            content = re.sub(r'</?s>', '', content)
            content = re.sub(r'<<SYS>>.*?<</SYS>>', '', content, flags=re.DOTALL)
            
            content = re.sub(r'\s+', ' ', content).strip()
            
            if not content or len(content.strip()) < 1:
                logger.warning(f"Empty content after parsing. Raw response: {response_body.get('generation', '')[:200]}")
                content = response_body.get('generation', 'No response generated').strip()
            elif content.count('<') > content.count(' '):
                logger.warning(f"Suspected parsing artifacts in content: {content[:100]}")
                content = response_body.get('generation', content).strip()
            
            return LLMResponse(
                content=content,
                model=self.model,
                usage=response_body.get("usage"),
                finish_reason="stop",  # Bedrock doesn't return explicit finish reason
                metadata={
                    "provider": "bedrock", 
                    "region": self.region,
                    "response_metadata": response_body
                }
            )
            
        except self.ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_msg = e.response.get('Error', {}).get('Message', str(e))
            logger.error(f"Bedrock API error [{error_code}]: {error_msg}")
            
            if error_code == 'ValidationException':
                raise ValueError(f"Invalid model or request: {error_msg}")
            elif error_code == 'ThrottlingException':
                raise Exception(f"Rate limit exceeded: {error_msg}")
            elif error_code == 'ModelNotReadyException':
                raise Exception(f"Model not ready: {error_msg}")
            else:
                raise Exception(f"Bedrock API error: {error_msg}")
                
        except Exception as e:
            logger.error(f"Unexpected Bedrock client error: {e}")
            raise
    
    def generate_text(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate response from text prompt."""
        _, HumanMessage, _, _ = _import_langchain()
        messages = [HumanMessage(content=prompt)]
        return self.generate(messages, **kwargs)


class LLaMAClient(LLMClient):
    """LLaMA API client with OpenAI-compatible interface."""
    
    def __init__(
        self,
        model: str = "llama-2-70b-chat",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 2048,
        **kwargs
    ):
        """
        Initialize LLaMA client.
        
        Args:
            model: LLaMA model name
            api_key: LLaMA API key
            api_base: LLaMA API base URL
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
        """
        requests = _import_requests()
        
        self.model = model
        self.api_key = api_key or os.getenv("LLAMA_API_KEY")
        self.api_base = api_base or os.getenv("LLAMA_API_BASE")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.session = requests.Session()
        
        if not self.api_key or not self.api_base:
            raise ValueError("LLaMA API key and base URL are required")
        
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
        
        logger.info(f"Initialized LLaMA client with model: {model}")
    
    def _format_messages_for_llama(self, messages: List[Any]) -> str:
        """
        Format LangChain messages for LLaMA chat format.
        
        LLaMA expects a specific chat format with system and user roles.
        """
        _, HumanMessage, SystemMessage, _ = _import_langchain()
        formatted_parts = []
        
        for message in messages:
            if isinstance(message, SystemMessage):
                formatted_parts.append(f"<s>[INST] <<SYS>>\n{message.content}\n<</SYS>>\n")
            elif isinstance(message, HumanMessage):
                if formatted_parts and not formatted_parts[-1].endswith("[/INST]"):
                    formatted_parts.append(f"{message.content} [/INST]")
                else:
                    formatted_parts.append(f"<s>[INST] {message.content} [/INST]")
            else:
                formatted_parts.append(f"<s>[INST] {message.content} [/INST]")
        
        return " ".join(formatted_parts)
    
    def generate(self, messages: List[Any], **kwargs) -> LLMResponse:
        """Generate response using LLaMA API."""
        try:
            requests = _import_requests()
            
            prompt = self._format_messages_for_llama(messages)
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "stream": False
            }
            
            response = self.session.post(
                f"{self.api_base}/completions",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            result = response.json()
            
            if "choices" not in result or not result["choices"]:
                raise ValueError("No choices in LLaMA API response")
            
            choice = result["choices"][0]
            content = choice.get("text", "").strip()
            
            return LLMResponse(
                content=content,
                model=self.model,
                usage=result.get("usage"),
                finish_reason=choice.get("finish_reason"),
                metadata={"provider": "llama", "api_base": self.api_base}
            )
            
        except Exception as e:
            if hasattr(e, 'response'):
                logger.error(f"LLaMA API request error: {e}")
            else:
                logger.error(f"LLaMA API error: {e}")
            raise
    
    def generate_text(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate response from text prompt."""
        _, HumanMessage, _, _ = _import_langchain()
        messages = [HumanMessage(content=prompt)]
        return self.generate(messages, **kwargs)


class LLMClientFactory:
    """Factory for creating LLM clients based on configuration."""
    
    @staticmethod
    def create_client(
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> LLMClient:
        """
        Create appropriate LLM client based on provider.
        
        Args:
            provider: API provider ('openai' or 'llama')
            model: Model name
            **kwargs: Additional client parameters
            
        Returns:
            Configured LLM client
        """
        if provider is None:
            provider = os.getenv("API_PROVIDER", "openai").lower()
        
        if model is None:
            model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        
        logger.info(f"Creating {provider} client with model: {model}")
        
        if provider.lower() == "openai":
            return OpenAIClient(model=model, **kwargs)
        elif provider.lower() == "anthropic":
            return AnthropicClient(model=model, **kwargs)
        elif provider.lower() == "bedrock":
            return BedrockClient(model=model, **kwargs)
        elif provider.lower() == "llama":
            logger.warning("LLaMA client is deprecated. Consider using 'bedrock' for AWS-hosted LLaMA models.")
            return LLaMAClient(model=model, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}. Use 'openai', 'anthropic', 'bedrock', or 'llama'")
    
    @staticmethod
    def get_available_models(provider: str) -> List[str]:
        """Get list of available models for a provider."""
        if provider.lower() == "openai":
            return [
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k", 
                "gpt-3.5-turbo-1106",
                "gpt-3.5-turbo-0125",
                "gpt-4",
                "gpt-4-32k",
                "gpt-4-1106-preview",
                "gpt-4-0125-preview",
                "gpt-4-turbo",
                "gpt-4-turbo-preview",
                "gpt-4o",
                "gpt-4o-mini"
            ]
        elif provider.lower() == "anthropic":
            return [
                "claude-3-haiku-20240307",
                "claude-3-sonnet-20240229", 
                "claude-3-opus-20240229",
                "claude-3-5-sonnet-20240620",
                "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku-20241022"
            ]
        elif provider.lower() == "bedrock":
            return [
                "meta.llama3-8b-instruct-v1:0",
                "meta.llama3-70b-instruct-v1:0",
                "meta.llama2-13b-chat-v1",
                "meta.llama2-70b-chat-v1",
            ]
        elif provider.lower() == "llama":
            return [
                "llama-2-7b-chat",
                "llama-2-13b-chat", 
                "llama-2-70b-chat",
                "llama-3-8b-instruct",
                "code-llama-7b-instruct",
                "code-llama-13b-instruct",
                "code-llama-34b-instruct"
            ]
        else:
            return []


def create_llm_client(**kwargs) -> LLMClient:
    """Create LLM client with environment-based configuration."""
    return LLMClientFactory.create_client(**kwargs)