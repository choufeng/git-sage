"""
ModelScope Chat Model Wrapper for LangChain integration
"""
from typing import Any, Dict, Iterator, List, Optional
import requests
import json
import os
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field


class ModelScopeChatModel(BaseChatModel):
    """ModelScope Chat Model implementation using DashScope API"""
    
    model_name: str = Field(default="qwen-max")
    api_key: str = Field(default="")
    base_url: str = Field(default="https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation")
    temperature: float = Field(default=0.5)
    max_tokens: Optional[int] = Field(default=None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 如果没有提供 API key，尝试从环境变量获取
        if not self.api_key:
            self.api_key = os.getenv("DASHSCOPE_API_KEY", "")
    
    @property
    def _llm_type(self) -> str:
        """Return identifier for the LLM."""
        return "modelscope-chat"
    
    def _convert_messages_to_prompt(self, messages: List[BaseMessage]) -> Dict[str, Any]:
        """Convert LangChain messages to ModelScope format"""
        formatted_messages = []
        
        for message in messages:
            if isinstance(message, HumanMessage):
                formatted_messages.append({
                    "role": "user", 
                    "content": message.content
                })
            elif isinstance(message, AIMessage):
                formatted_messages.append({
                    "role": "assistant",
                    "content": message.content
                })
            elif isinstance(message, SystemMessage):
                formatted_messages.append({
                    "role": "system",
                    "content": message.content
                })
        
        return {
            "model": self.model_name,
            "input": {
                "messages": formatted_messages
            },
            "parameters": {
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
        }
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Call ModelScope API and return result"""
        
        if not self.api_key:
            raise ValueError("API key is required for ModelScope. Set DASHSCOPE_API_KEY environment variable or provide api_key parameter.")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = self._convert_messages_to_prompt(messages)
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 解析响应
            if result.get("status_code") == 200:
                output_text = result["output"]["text"]
                message = AIMessage(content=output_text)
                generation = ChatGeneration(message=message)
                return ChatResult(generations=[generation])
            else:
                error_msg = result.get("message", "Unknown error")
                raise Exception(f"ModelScope API error: {error_msg}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to call ModelScope API: {str(e)}")
        except KeyError as e:
            raise Exception(f"Unexpected response format from ModelScope API: {str(e)}")


class ModelScopeInferenceChatModel(BaseChatModel):
    """ModelScope Chat Model implementation using Inference API (alternative endpoint)"""
    
    model_name: str = Field(default="qwen/Qwen2.5-Coder-32B-Instruct")
    api_key: str = Field(default="")
    base_url: str = Field(default="https://api-inference.modelscope.cn/v1/chat/completions")
    temperature: float = Field(default=0.5)
    max_tokens: Optional[int] = Field(default=2048)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 如果没有提供 API key，尝试从环境变量获取
        if not self.api_key:
            self.api_key = os.getenv("MODELSCOPE_API_KEY", "")
    
    @property
    def _llm_type(self) -> str:
        """Return identifier for the LLM."""
        return "modelscope-inference-chat"
    
    def _convert_messages_to_openai_format(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        """Convert LangChain messages to OpenAI-compatible format"""
        formatted_messages = []
        
        for message in messages:
            if isinstance(message, HumanMessage):
                formatted_messages.append({
                    "role": "user", 
                    "content": message.content
                })
            elif isinstance(message, AIMessage):
                formatted_messages.append({
                    "role": "assistant",
                    "content": message.content
                })
            elif isinstance(message, SystemMessage):
                formatted_messages.append({
                    "role": "system",
                    "content": message.content
                })
        
        return formatted_messages
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Call ModelScope Inference API and return result"""
        
        if not self.api_key:
            raise ValueError("API key is required for ModelScope. Set MODELSCOPE_API_KEY environment variable or provide api_key parameter.")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "messages": self._convert_messages_to_openai_format(messages),
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 解析OpenAI格式的响应
            if "choices" in result and len(result["choices"]) > 0:
                output_text = result["choices"][0]["message"]["content"]
                message = AIMessage(content=output_text)
                generation = ChatGeneration(message=message)
                return ChatResult(generations=[generation])
            else:
                error_msg = result.get("error", {}).get("message", "Unknown error")
                raise Exception(f"ModelScope API error: {error_msg}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to call ModelScope API: {str(e)}")
        except KeyError as e:
            raise Exception(f"Unexpected response format from ModelScope API: {str(e)}")
