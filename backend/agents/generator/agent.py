"""
Generator agent implementation using A2A protocol.
This agent is responsible for generating answers based on retrieved Quranic context.
"""

import asyncio
from typing import Any, Dict, List, Optional

from backend.agents.base import BaseAgent, AgentRequest, AgentResponse
from backend.core.generator import (
    create_answer_generator,
    generate_answer,
    process_query
)
from backend.core.llm_client import get_chat_model


class GeneratorAgentRequest(AgentRequest):
    """Specialized request model for the generator agent."""
    context: str
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.0
    max_tokens: int = 1000


class GeneratorAgentResponse(AgentResponse):
    """Specialized response model for the generator agent."""
    answer: str
    sources: Optional[List[Dict[str, Any]]] = None


class GeneratorAgent(BaseAgent):
    """Agent responsible for generating answers based on retrieved Quranic context."""
    
    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.0,
        max_tokens: int = 1000,
        name: str = "quran-generator",
        description: str = "Generates answers to questions about the Quran based on provided context"
    ):
        """
        Initialize the generator agent.
        
        Args:
            model_name: Name of the LLM to use
            temperature: Temperature parameter for generation
            max_tokens: Maximum tokens to generate
            name: The name of the agent
            description: A description of the agent's capabilities
        """
        super().__init__(name, description)
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._initialize_generator()
        
    def _initialize_generator(self):
        """Initialize the answer generator chain."""
        try:
            self.generator = create_answer_generator(
                model_name=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            print(f"Initialized generator with model {self.model_name}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize generator: {e}")
    
    async def process(self, request: GeneratorAgentRequest) -> GeneratorAgentResponse:
        """
        Process a generation request and return an answer based on the provided context.
        
        Args:
            request: The generation request containing query and context
            
        Returns:
            A response containing the generated answer
        """
        # Extract parameters
        query = request.query
        context = request.parameters.get("context", request.context) if request.parameters else request.context
        
        # Update generator if model parameters changed
        model_name = request.parameters.get("model_name", self.model_name) if request.parameters else self.model_name
        temperature = request.parameters.get("temperature", self.temperature) if request.parameters else self.temperature
        max_tokens = request.parameters.get("max_tokens", self.max_tokens) if request.parameters else self.max_tokens
        
        if (model_name != self.model_name or 
            temperature != self.temperature or 
            max_tokens != self.max_tokens):
            self.model_name = model_name
            self.temperature = temperature
            self.max_tokens = max_tokens
            self._initialize_generator()
            
        # Run the generation process in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        answer = await loop.run_in_executor(
            None,
            lambda: generate_answer(self.generator, context, query)
        )
        
        # Extract sources from context (if available)
        sources = []
        for line in context.split("\n\n"):
            if line.startswith("[") and "]:" in line:
                reference_part = line.split("]:")[0][1:]
                content_part = line.split("]:")[1].strip()
                
                if " " in reference_part:
                    source_type, reference = reference_part.split(" ", 1)
                    sources.append({
                        "source_type": source_type,
                        "reference": reference,
                        "content": content_part
                    })
                    
        return GeneratorAgentResponse(
            content=answer,
            metadata={"query": query, "model": self.model_name},
            answer=answer,
            sources=sources
        )
    
    def get_capabilities(self) -> List[str]:
        """
        Get the list of capabilities this agent provides.
        
        Returns:
            A list of capability strings
        """
        return [
            "answer-generation",
            "quran-interpretation",
            "tafsir-explanation",
            "multi-model-support"
        ]