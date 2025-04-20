"""
Base agent interface for RAG Quran using A2A protocol.
This module provides the foundation for all agent implementations in the system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class AgentRequest(BaseModel):
    """Base model for agent requests."""
    query: str
    parameters: Optional[Dict[str, Any]] = None
    
    
class AgentResponse(BaseModel):
    """Base model for agent responses."""
    content: Any
    metadata: Optional[Dict[str, Any]] = None


class BaseAgent(ABC):
    """Base agent interface that all specialized agents must implement."""
    
    def __init__(self, name: str, description: str):
        """
        Initialize the base agent.
        
        Args:
            name: The name of the agent
            description: A description of the agent's capabilities
        """
        self.name = name
        self.description = description
        
    @abstractmethod
    async def process(self, request: AgentRequest) -> AgentResponse:
        """
        Process a request and return a response.
        
        Args:
            request: The request to process
            
        Returns:
            A response containing the processed result
        """
        pass
    
    def get_agent_card(self) -> Dict[str, Any]:
        """
        Get the agent card describing this agent's capabilities.
        
        Returns:
            A dictionary containing the agent's metadata
        """
        return {
            "name": self.name,
            "description": self.description,
            "version": "1.0.0",
            "contact": {
                "name": "RAG Quran Team"
            }
        }
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Get the list of capabilities this agent provides.
        
        Returns:
            A list of capability strings
        """
        pass