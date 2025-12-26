"""
LLM Client Service for OpenAI/Azure OpenAI integration with Elite Resilience
"""
import asyncio
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI, AsyncAzureOpenAI
import json
import os
from dotenv import load_dotenv
load_dotenv()

from backend.config import config
from backend.models.schemas import ChatMessage, MessageRole

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from tenacity import retry, stop_after_attempt, wait_exponential
from google.api_core.exceptions import ResourceExhausted

class LLMClient:
    """Client for interacting with LLM providers"""
    
    def __init__(self):
        """Initialize LLM client based on configuration"""
        google_key = os.getenv("GOOGLE_API_KEY")
        
        if config.AZURE_OPENAI_API_KEY:
            self.client = AsyncAzureOpenAI(
                api_key=config.AZURE_OPENAI_API_KEY,
                api_version="2024-02-15-preview",
                azure_endpoint=config.AZURE_OPENAI_ENDPOINT
            )
            self.model = config.AZURE_OPENAI_DEPLOYMENT
            self.provider = "azure"
        elif google_key:
            self.client = ChatGoogleGenerativeAI(
                model="gemini-flash-latest",
                google_api_key=google_key,
                temperature=config.TEMPERATURE,
                convert_system_message_to_human=True
            )
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=google_key
            )
            self.model = "gemini-flash-latest"
            self.provider = "google"
        elif config.OPENAI_API_KEY:
            self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
            self.model = config.OPENAI_MODEL
            self.provider = "openai"
        else:
            raise ValueError("No LLM API key configured")
    
    async def generate_response(
        self,
        messages: List[ChatMessage],
        system_prompt: str,
        temperature: float = None,
        max_tokens: int = None,
        stream: bool = False
    ) -> str:
        """
        Generate a response from the LLM with Elite Resilience (auto-retry on rate limits)
        
        Args:
            messages: Conversation history
            system_prompt: System prompt for the LLM
            temperature: Sampling temperature (default from config)
            max_tokens: Max tokens to generate (default from config)
            stream: Whether to stream the response
        
        Returns:
            Generated response text
        """
        temperature = temperature or config.TEMPERATURE
        max_tokens = max_tokens or config.MAX_TOKENS
        
        if self.provider == "google":
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
            
            lc_messages = [SystemMessage(content=system_prompt)]
            for msg in messages:
                if isinstance(msg, dict):
                    role = msg.get("role")
                    content = msg.get("content")
                else:
                    role = msg.role.value if hasattr(msg.role, 'value') else msg.role
                    content = msg.content
                
                if role == "user":
                    lc_messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    lc_messages.append(AIMessage(content=content))
                else:
                    lc_messages.append(HumanMessage(content=f"[{role}]: {content}"))
            
            # Apply retry logic for Google API with Elite Resilience
            @retry(
                stop=stop_after_attempt(5),
                wait=wait_exponential(multiplier=1, min=2, max=20),
                retry=lambda e: isinstance(e, ResourceExhausted)
            )
            async def _invoke_with_retry():
                return await self.client.ainvoke(lc_messages, temperature=temperature, max_output_tokens=max_tokens)
            
            response = await _invoke_with_retry()
            return response.content

        # Format messages for OpenAI API
        formatted_messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        for msg in messages:
            # Handle both dict and ChatMessage objects
            if isinstance(msg, dict):
                role = msg.get("role")
                content = msg.get("content")
            else:
                role = msg.role.value if hasattr(msg.role, 'value') else msg.role
                content = msg.content
            
            formatted_messages.append({
                "role": role,
                "content": content
            })
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=config.TOP_P,
                stream=stream
            )
            
            if stream:
                return response  # Return stream object
            else:
                return response.choices[0].message.content
        
        except Exception as e:
            raise Exception(f"LLM API error: {str(e)}")
    
    async def generate_with_json_response(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful assistant that responds in JSON format."
    ) -> Dict[str, Any]:
        """
        Generate a JSON response from the LLM with Elite Resilience
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
        
        Returns:
            Parsed JSON response
        """
        if self.provider == "google":
            from langchain_core.messages import HumanMessage, SystemMessage
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt + "\n\nIMPORTANT: Return ONLY a valid JSON object.")
            ]
            
            # Apply retry logic for Google API with Elite Resilience
            @retry(
                stop=stop_after_attempt(5),
                wait=wait_exponential(multiplier=1, min=2, max=20),
                retry=lambda e: isinstance(e, ResourceExhausted)
            )
            async def _invoke_with_retry():
                return await self.client.ainvoke(messages, temperature=0.1)
            
            response = await _invoke_with_retry()
            content = response.content
            # Clean up potential markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Try to find JSON-like structure if parsing fails
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                raise

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Lower temperature for structured output
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
        
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {str(e)}")
        except Exception as e:
            raise Exception(f"LLM API error: {str(e)}")
    
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embeddings for text
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector
        """
        try:
            if self.provider == "google":
                return await self.embeddings.aembed_query(text)
            
            if self.provider == "azure":
                response = await self.client.embeddings.create(
                    input=text,
                    model="text-embedding-ada-002"
                )
            else:
                response = await self.client.embeddings.create(
                    input=text,
                    model="text-embedding-3-small"
                )
            
            return response.data[0].embedding
        
        except Exception as e:
            raise Exception(f"Embedding API error: {str(e)}")
    
    async def stream_response(
        self,
        messages: List[ChatMessage],
        system_prompt: str,
        temperature: float = None
    ):
        """
        Stream response from LLM
        
        Args:
            messages: Conversation history
            system_prompt: System prompt
            temperature: Sampling temperature
        
        Yields:
            Response chunks
        """
        temperature = temperature or config.TEMPERATURE
        
        if self.provider == "google":
            from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
            lc_messages = [SystemMessage(content=system_prompt)]
            for msg in messages:
                role = msg.role.value if hasattr(msg.role, 'value') else msg.role
                if role == "user":
                    lc_messages.append(HumanMessage(content=msg.content))
                elif role == "assistant":
                    lc_messages.append(AIMessage(content=msg.content))
                else:
                    lc_messages.append(HumanMessage(content=f"[{role}]: {msg.content}"))
            
            # Apply retry logic for Google API streaming with Elite Resilience
            @retry(
                stop=stop_after_attempt(5),
                wait=wait_exponential(multiplier=1, min=2, max=20),
                retry=lambda e: isinstance(e, ResourceExhausted)
            )
            async def _stream_with_retry():
                result = []
                async for chunk in self.client.astream(lc_messages, temperature=temperature):
                    result.append(chunk.content)
                return result
            
            chunks = await _stream_with_retry()
            for chunk in chunks:
                yield chunk
            return

        formatted_messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        for msg in messages:
            formatted_messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=config.MAX_TOKENS,
                top_p=config.TOP_P,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        except Exception as e:
            raise Exception(f"LLM streaming error: {str(e)}")


# Singleton instance
llm_client = LLMClient()
