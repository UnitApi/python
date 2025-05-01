from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class DSLElement:
    """Base class for all DSL elements"""

    type: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Extension:
    """Extension configuration"""

    type: str = "extension"
    name: str = None
    version: str = None
    config: Dict[str, Any] = field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.name is None or self.version is None:
            raise ValueError("Extension must have a name and version")


@dataclass
class Device:
    """Device configuration"""

    type: str = "device"
    id: str = None
    device_type: str = None
    capabilities: List[str] = field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.id is None or self.device_type is None:
            raise ValueError("Device must have an id and device_type")


@dataclass
class PipelineStep:
    """Single step in pipeline"""

    type: str = "step"
    action: str = None
    params: Dict[str, Any] = field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.action is None:
            raise ValueError("PipelineStep must have an action")


@dataclass
class Pipeline:
    """Pipeline configuration"""

    type: str = "pipeline"
    name: str = None
    source: Optional[str] = None
    target: Optional[str] = None
    steps: List[PipelineStep] = field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.name is None:
            raise ValueError("Pipeline must have a name")


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
        raise NotImplementedError(
            f"to_string not implemented for {self.__class__.__name__}"
        )
