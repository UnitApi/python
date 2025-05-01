from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class DSLElement:
    """Base class for all DSL elements"""
    type: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Extension(DSLElement):
    """Extension configuration"""
    name: str
    version: str
    config: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class Device(DSLElement):
    """Device configuration"""
    id: str
    device_type: str
    capabilities: List[str] = field(default_factory=list)
    
@dataclass
class PipelineStep(DSLElement):
    """Single step in pipeline"""
    action: str
    params: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class Pipeline(DSLElement):
    """Pipeline configuration"""
    name: str
    source: Optional[str] = None
    target: Optional[str] = None
    steps: List[PipelineStep] = field(default_factory=list)

class IDSLParser(ABC):
    """Interface for DSL parsers"""
    
    @abstractmethod
    def parse(self, content: str) -> Dict[str, Any]:
        """
        Parse DSL content into a standardized dictionary structure.
        
        Args:
            content: The DSL content as a string
            
        Returns:
            A dictionary containing the parsed configuration
        """
        pass
    
    @abstractmethod
    def validate(self, config: Dict[str, Any]) -> bool:
        """
        Validate parsed configuration against schema.
        
        Args:
            config: The parsed configuration dictionary
            
        Returns:
            True if the configuration is valid, False otherwise
        """
        pass
    
    def to_string(self, config: Dict[str, Any]) -> str:
        """
        Convert a configuration dictionary back to DSL string format.
        
        Args:
            config: The configuration dictionary to convert
            
        Returns:
            The DSL content as a string
        """
        raise NotImplementedError(f"to_string not implemented for {self.__class__.__name__}")
