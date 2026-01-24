from abc import ABC, abstractmethod
from typing import Any, Dict

class JobAgentTool(ABC):
    """Base class ensuring tool independence."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        pass

    @abstractmethod
    def validate_input(self, **kwargs) -> bool:
        pass
