"""
AWS Bedrock client implementation for LLaMA models.

Provides integration with AWS Bedrock hosted LLaMA models using boto3.
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional

from .base import LLMClient, LLMResponse
from .config import BedrockConfig
from .exceptions import LLMError, LLMAuthenticationError, LLMValidationError

logger = logging.getLogger(__name__)


def _import_boto3():
    """Lazy import of boto3."""
    try:
        import boto3
        from botocore.exceptions import ClientError
        return boto3, ClientError
    except ImportError as e:
        raise ImportError(
            "boto3 is required for AWS Bedrock. Install with: pip install boto3"
        ) from e


def _import_langchain():
    """Lazy import of LangChain message types."""
    try:
        from langchain.schema import HumanMessage, SystemMessage
        return HumanMessage, SystemMessage
    except ImportError as e:
        raise ImportError(
            "langchain is required. Install with: pip install langchain"
        ) from e


class BedrockClient(LLMClient):
    """AWS Bedrock client for LLaMA and Claude models using boto3."""

    DEFAULT_MODELS = {
        "meta.llama3-8b-instruct-v1:0": 2048,
        "meta.llama3-70b-instruct-v1:0": 4096,
        "meta.llama2-13b-chat-v1": 2048,
        "meta.llama2-70b-chat-v1": 4096,
        "anthropic.claude-3-haiku-20240307-v1:0": 4096,
        "anthropic.claude-3-sonnet-20240229-v1:0": 4096,
        "anthropic.claude-3-opus-20240229-v1:0": 4096,
        "anthropic.claude-3-5-sonnet-20240620-v1:0": 4096,
    }

    def __init__(
        self,
        model: str = "anthropic.claude-3-haiku-20240307-v1:0",
        region_name: Optional[str] = None,
        aws_profile: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 2048,
        **kwargs
    ) -> None:
        """Initialize AWS Bedrock client."""
        boto3, ClientError = _import_boto3()

        self.config = BedrockConfig(
            model=model,
            region_name=region_name,
            aws_profile=aws_profile,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_params=kwargs
        )

        self.model = model
        self.temperature = temperature
        self.max_tokens = self.config.max_tokens
        self.ClientError = ClientError
        self.region = region_name or os.getenv("AWS_REGION", "us-east-1")
        self.is_claude = model.startswith("anthropic.")

        try:
            if aws_profile:
                session = boto3.Session(profile_name=aws_profile)
                self.client = session.client("bedrock-runtime", region_name=self.region)
            else:
                self.client = boto3.client("bedrock-runtime", region_name=self.region)
        except Exception as e:
            raise LLMAuthenticationError(
                "Failed to initialize AWS Bedrock client",
                api_key_hint="Ensure AWS credentials configured via 'aws configure' or IAM roles",
                provider="bedrock",
                model=model
            ) from e

        logger.info(f"Initialized Bedrock client: model={model}, region={self.region}")

    @property
    def provider_name(self) -> str:
        return "bedrock"

    @property
    def model_name(self) -> str:
        return self.model

    def _format_messages_for_llama(self, messages: List[Any]) -> str:
        """Format LangChain messages for Bedrock LLaMA models."""
        HumanMessage, SystemMessage = _import_langchain()

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
            return f"<s>[INST] <<SYS>>\n{system_message}\n<</SYS>>\n\n{user_content} [/INST]"
        else:
            return f"<s>[INST] {user_content} [/INST]"

    def _format_messages_for_claude(self, messages: List[Any]) -> tuple[str, List[Dict[str, str]]]:
        """Format LangChain messages for Bedrock Claude models."""
        HumanMessage, SystemMessage = _import_langchain()

        system_message = None
        formatted_messages = []

        for message in messages:
            if isinstance(message, SystemMessage):
                system_message = message.content
            elif isinstance(message, HumanMessage):
                formatted_messages.append({"role": "user", "content": message.content})
            else:
                content = str(message.content) if hasattr(message, 'content') else str(message)
                formatted_messages.append({"role": "user", "content": content})

        return system_message, formatted_messages

    def _clean_response(self, content: str) -> str:
        """Clean Bedrock response from formatting artifacts."""
        import re

        # Remove common prefixes
        if content.startswith("### Response:"):
            content = content.replace("### Response:", "").strip()

        # Remove instructional echoes
        lines = content.split('\n')
        clean_lines = []

        for line in lines:
            line = line.strip()
            if (line.startswith('Rank these products') or
                line.startswith('Here are some products') or
                'in order of preference:' in line):
                continue
            if line and not line.startswith('[') and not line.startswith('<'):
                clean_lines.append(line)

        if clean_lines:
            content = '\n'.join(clean_lines)

        # Remove instruction tags
        content = re.sub(r'\[/?INST\]', '', content)
        content = re.sub(r'\[/?s\]', '', content)
        content = re.sub(r'</?s>', '', content)
        content = re.sub(r'<<SYS>>.*?<</SYS>>', '', content, flags=re.DOTALL)

        # Normalize whitespace
        content = re.sub(r'\s+', ' ', content).strip()

        return content

    def generate(self, messages: List[Any], **kwargs) -> LLMResponse:
        """Generate response using AWS Bedrock."""
        try:
            if self.is_claude:
                return self._generate_claude(messages, **kwargs)
            else:
                return self._generate_llama(messages, **kwargs)
        except self.ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_msg = e.response.get('Error', {}).get('Message', str(e))
            logger.error(f"Bedrock API error [{error_code}]: {error_msg}")

            if error_code == 'ValidationException':
                raise LLMValidationError(
                    f"Invalid model or request: {error_msg}",
                    provider="bedrock",
                    model=self.model
                )
            elif error_code == 'ThrottlingException':
                raise LLMError(
                    f"Rate limit exceeded: {error_msg}",
                    provider="bedrock",
                    model=self.model
                )
            elif error_code == 'ModelNotReadyException':
                raise LLMError(
                    f"Model not ready: {error_msg}",
                    provider="bedrock",
                    model=self.model
                )
            else:
                raise LLMError(
                    f"Bedrock API error: {error_msg}",
                    provider="bedrock",
                    model=self.model
                )

        except Exception as e:
            logger.error(f"Unexpected Bedrock error: {e}")
            raise LLMError(
                f"Bedrock client error: {e}",
                provider="bedrock",
                model=self.model
            ) from e

    def _generate_llama(self, messages: List[Any], **kwargs) -> LLMResponse:
        """Generate response using LLaMA models."""
        prompt = self._format_messages_for_llama(messages)

        request_body = {
            "prompt": prompt,
            "max_gen_len": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "top_p": kwargs.get("top_p", 0.9),
        }

        response = self.client.invoke_model(
            modelId=self.model,
            body=json.dumps(request_body),
            accept="application/json",
            contentType="application/json"
        )

        response_body = json.loads(response["body"].read())

        if "generation" not in response_body:
            raise LLMValidationError(
                "No generation found in Bedrock response",
                provider="bedrock",
                model=self.model
            )

        content = self._clean_response(response_body["generation"])

        if not content or len(content.strip()) < 1:
            logger.warning(f"Empty content after parsing. Raw: {response_body.get('generation', '')[:200]}")
            content = response_body.get('generation', 'No response generated').strip()

        return LLMResponse(
            content=content,
            model=self.model,
            usage=response_body.get("usage"),
            finish_reason="stop",
            metadata={
                "provider": "bedrock",
                "region": self.region,
                "response_metadata": response_body
            }
        )

    def _generate_claude(self, messages: List[Any], **kwargs) -> LLMResponse:
        """Generate response using Claude models."""
        system_message, formatted_messages = self._format_messages_for_claude(messages)

        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": formatted_messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
        }

        if system_message:
            request_body["system"] = system_message

        response = self.client.invoke_model(
            modelId=self.model,
            body=json.dumps(request_body),
            accept="application/json",
            contentType="application/json"
        )

        response_body = json.loads(response["body"].read())

        if "content" not in response_body:
            raise LLMValidationError(
                "No content found in Bedrock Claude response",
                provider="bedrock",
                model=self.model
            )

        content = response_body["content"][0]["text"]

        return LLMResponse(
            content=content,
            model=self.model,
            usage=response_body.get("usage"),
            finish_reason=response_body.get("stop_reason", "stop"),
            metadata={
                "provider": "bedrock",
                "region": self.region,
                "response_metadata": response_body
            }
        )

    def generate_text(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate response from text prompt."""
        HumanMessage, _ = _import_langchain()
        messages = [HumanMessage(content=prompt)]
        return self.generate(messages, **kwargs)
