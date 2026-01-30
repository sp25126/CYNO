"""
CYNO Base Tool Classes
Provides base classes for all CYNO tools.
"""


class JobAgentTool:
    """Base class for all CYNO job agent tools."""
    
    name: str = "base_tool"
    description: str = "Base tool class"
    
    def execute(self, *args, **kwargs):
        """Execute the tool. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement execute()")
    
    def __str__(self):
        return f"<{self.__class__.__name__}>"
    
    def __repr__(self):
        return self.__str__()
