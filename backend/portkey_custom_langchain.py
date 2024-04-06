from typing import Any, Dict, List, Optional

from langchain_core.language_models.llms import LLM

from portkey_ai import Portkey, AsyncPortkey

from langchain_core.callbacks import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain.schema.messages import HumanMessage, SystemMessage, AIMessage, ChatMessage, FunctionMessage, ToolMessage, BaseMessage

def convert_message_to_dict(message: BaseMessage) -> dict:
    """Convert a LangChain message to a dictionary.

    Args:
        message: The LangChain message.

    Returns:
        The dictionary.
    """
    message_dict: Dict[str, Any] = {
        "content": message.content,
    }
    if (name := message.name or message.additional_kwargs.get("name")) is not None:
        message_dict["name"] = name

    # populate role and additional message data
    if isinstance(message, ChatMessage):
        message_dict["role"] = message.role
    elif isinstance(message, HumanMessage):
        message_dict["role"] = "user"
    elif isinstance(message, AIMessage):
        message_dict["role"] = "assistant"
        if "function_call" in message.additional_kwargs:
            message_dict["function_call"] = message.additional_kwargs["function_call"]
            # If function call only, content is None not empty string
            if message_dict["content"] == "":
                message_dict["content"] = None
        if "tool_calls" in message.additional_kwargs:
            message_dict["tool_calls"] = message.additional_kwargs["tool_calls"]
            # If tool calls only, content is None not empty string
            if message_dict["content"] == "":
                message_dict["content"] = None
    elif isinstance(message, SystemMessage):
        message_dict["role"] = "system"
    elif isinstance(message, FunctionMessage):
        message_dict["role"] = "function"
    elif isinstance(message, ToolMessage):
        message_dict["role"] = "tool"
        message_dict["tool_call_id"] = message.tool_call_id

        supported_props = {"content", "role", "tool_call_id"}
        message_dict = {k: v for k, v in message_dict.items() if k in supported_props}
    else:
        raise TypeError(f"Got unknown type {message}")
    return message_dict


class CustomPortkeyLLM(LLM):
    client: Optional[Portkey] = None
    async_client: Optional[AsyncPortkey] = None
    model: str
    temperature: float = 0
    trace_id: str = None
    metadata: dict = None
    max_tokens: int = None

    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        trace_id: str = None,
        metadata: dict = None,
        **kwargs: Any,
    ) -> str:
        """Call the language model."""
        if self.client is None:
            raise ValueError("The 'client' attribute must be set before calling '_call'.")

        # Create a dictionary to store the keyword arguments
        completion_kwargs = {
            "messages": [{"role": "user", "content": prompt}],
            "model": self.model,
            "temperature": self.temperature,
            **kwargs
        }

        # Add the 'stop' parameter only if it exists
        if stop is not None:
            completion_kwargs["stop"] = stop
        
        # Add the 'max_tokens' parameter only if it exists
        if self.max_tokens is not None:
            completion_kwargs["max_tokens"] = self.max_tokens

        completion = self.client.with_options(
            trace_id = trace_id or self.trace_id, 
            metadata = metadata or self.metadata,
        ).chat.completions.create(**completion_kwargs)
        
        return completion.choices[0].message.content

    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        trace_id: str = None,
        metadata: dict = None,
        **kwargs: Any,
    ) -> str:
        """Call the language model asynchronously."""
        if self.async_client is None:
            raise ValueError("The 'async_client' attribute must be set before calling '_acall'.")

        # Create a dictionary to store the keyword arguments
        completion_kwargs = {
            "messages": [{"role": "user", "content": prompt}],
            "model": self.model,
            "temperature": self.temperature,
            **kwargs
        }

        # Add the 'stop' parameter only if it exists
        if stop is not None:
            completion_kwargs["stop"] = stop
            
        # Add the 'max_tokens' parameter only if it exists
        if self.max_tokens is not None:
            completion_kwargs["max_tokens"] = self.max_tokens

        completion = await self.async_client.with_options(
            trace_id = trace_id or self.trace_id, 
            metadata = metadata or self.metadata,
        ).chat.completions.create(**completion_kwargs)
        
        return completion.choices[0].message.content
    
    

class CustomPortkeyChatModel(BaseChatModel):
    """A custom implementation of portkey wrapper.
    """
    client: Optional[Portkey] = None
    """The portkey client for synchronous calls."""
    async_client: Optional[AsyncPortkey] = None
    """The portkey client for asynchronous calls."""
    model: str
    """The model name passed to portkey."""
    temperature: float = 0
    trace_id: str = None
    metadata: dict = None
    max_tokens: int = None
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        trace_id: str = None,
        metadata: dict = None,
        **kwargs: Any,
    ) -> ChatResult:
        
        # convert the messages to a list of dicts
        transformed_messages = [convert_message_to_dict(message) for message in messages]
        
        """Call the language model."""
        if self.client is None:
            raise ValueError("The 'client' attribute must be set before calling '_call'.")

        # Create a dictionary to store the keyword arguments
        completion_kwargs = {
            "messages": transformed_messages,
            "model": self.model,
            "temperature": self.temperature,
            **kwargs
        }

        # Add the 'stop' parameter only if it exists
        if stop is not None:
            completion_kwargs["stop"] = stop
            
        # Add the 'max_tokens' parameter only if it exists
        if self.max_tokens is not None:
            completion_kwargs["max_tokens"] = self.max_tokens

        # print(f"completion_kwargs: {completion_kwargs}")
        completion = self.client.with_options(
            trace_id = trace_id or self.trace_id, 
            metadata = metadata or self.metadata,
        ).chat.completions.create(**completion_kwargs)
        
        message = AIMessage(content=completion.choices[0].message.content)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])


    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        trace_id: str = None,
        metadata: dict = None,
        **kwargs: Any,
    ) -> ChatResult:
        
        # convert the messages to a list of dicts
        transformed_messages = [convert_message_to_dict(message) for message in messages]
        
        """Call the language model asynchronously."""
        if self.async_client is None:
            raise ValueError("The 'async_client' attribute must be set before calling '_acall'.")

        # Create a dictionary to store the keyword arguments
        completion_kwargs = {
            "messages": transformed_messages,
            "model": self.model,
            "temperature": self.temperature,
            **kwargs
        }

        # Add the 'stop' parameter only if it exists
        if stop is not None:
            completion_kwargs["stop"] = stop
            
        # Add the 'max_tokens' parameter only if it exists
        if self.max_tokens is not None:
            completion_kwargs["max_tokens"] = self.max_tokens

        # print(f"completion_kwargs: {completion_kwargs}")
        completion = await self.async_client.with_options(
            trace_id = trace_id or self.trace_id, 
            metadata = metadata or self.metadata,
        ).chat.completions.create(**completion_kwargs)
        
        message = AIMessage(content=completion.choices[0].message.content)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])
    

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model."""
        return f"portkey:{self.model}"
