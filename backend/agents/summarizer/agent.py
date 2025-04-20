"""
Summarizer agent implementation using A2A protocol.
This agent is responsible for summarizing Quranic content or tafsirs.
"""

import asyncio
from typing import Any, Dict, List, Optional

from backend.agents.base import BaseAgent, AgentRequest, AgentResponse
from backend.core.llm_client import get_chat_model


class SummarizerAgentRequest(AgentRequest):
    """Specialized request model for the summarizer agent."""
    content: str
    max_length: Optional[int] = 200  # Maximum length of summary in words
    focus: Optional[str] = None  # Optional focus for the summary (e.g., "historical context")
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.3


class SummarizerAgentResponse(AgentResponse):
    """Specialized response model for the summarizer agent."""
    summary: str
    original_length: int  # Length of original content in words
    summary_length: int  # Length of summary in words


class SummarizerAgent(BaseAgent):
    """Agent responsible for summarizing Quranic content or tafsirs."""
    
    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.3,
        name: str = "quran-summarizer",
        description: str = "Summarizes Quranic passages or tafsirs with customizable length and focus"
    ):
        """
        Initialize the summarizer agent.
        
        Args:
            model_name: Name of the LLM to use
            temperature: Temperature parameter for generation
            name: The name of the agent
            description: A description of the agent's capabilities
        """
        super().__init__(name, description)
        self.model_name = model_name
        self.temperature = temperature
        
    async def process(self, request: SummarizerAgentRequest) -> SummarizerAgentResponse:
        """
        Process a summarization request and return a summary of the provided content.
        
        Args:
            request: The summarization request containing content to summarize
            
        Returns:
            A response containing the generated summary
        """
        # Extract parameters
        content = request.parameters.get("content", request.content) if request.parameters else request.content
        max_length = request.parameters.get("max_length", 200) if request.parameters else getattr(request, "max_length", 200)
        focus = request.parameters.get("focus", None) if request.parameters else getattr(request, "focus", None)
        model_name = request.parameters.get("model_name", self.model_name) if request.parameters else getattr(request, "model_name", self.model_name)
        temperature = request.parameters.get("temperature", self.temperature) if request.parameters else getattr(request, "temperature", self.temperature)
        
        # Count words in original content
        original_length = len(content.split())
        
        # Create the summarization prompt
        focus_instruction = f" with a focus on {focus}" if focus else ""
        system_prompt = (
            f"You are a specialized summarization assistant for Quranic content and Islamic texts. "
            f"Summarize the following content in about {max_length} words or less{focus_instruction}. "
            f"Maintain the key theological points and spiritual essence while being concise."
        )
        
        # Get the chat model
        chat_model = get_chat_model(model_name=model_name, temperature=temperature)
        
        # Create the messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
        ]
        
        # Run the summarization process in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: chat_model.generate_content(messages).text
        )
        
        # Count words in summary
        summary_length = len(response.split())
        
        return SummarizerAgentResponse(
            content=response,
            metadata={
                "original_length": original_length,
                "summary_length": summary_length,
                "focus": focus,
                "model": model_name
            },
            summary=response,
            original_length=original_length,
            summary_length=summary_length
        )
    
    def get_capabilities(self) -> List[str]:
        """
        Get the list of capabilities this agent provides.
        
        Returns:
            A list of capability strings
        """
        return [
            "content-summarization",
            "tafsir-summarization",
            "length-controlled-summarization",
            "focused-summarization"
        ]