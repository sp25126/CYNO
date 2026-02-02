"""
Tool Registry for dynamic tool management.
Allows adding/removing tools without modifying core agent code.
"""
from typing import Dict, Type, Any, Optional
from tools.base import JobAgentTool


class ToolRegistry:
    """Singleton registry for all agent tools."""
    
    _tools: Dict[str, Type[JobAgentTool]] = {}
    _instances: Dict[str, JobAgentTool] = {}  # Cache instances for performance
    
    @classmethod
    def register(cls, name: str):
        """
        Decorator to register a tool.
        Usage:
            @ToolRegistry.register("parse_resume")
            class ResumeParserTool(JobAgentTool):
                ...
        """
        def decorator(tool_class: Type[JobAgentTool]):
            cls._tools[name] = tool_class
            return tool_class
        return decorator
    
    @classmethod
    def register_instance(cls, name: str, tool_class: Type[JobAgentTool]):
        """Programmatically register a tool class."""
        cls._tools[name] = tool_class
    
    @classmethod
    def get(cls, name: str, **init_kwargs) -> Optional[JobAgentTool]:
        """
        Get a tool instance by name.
        Creates and caches instance on first access.
        """
        if name not in cls._tools:
            return None
        
        # Return cached instance if no custom init params
        if not init_kwargs and name in cls._instances:
            return cls._instances[name]
        
        # Create new instance
        tool = cls._tools[name](**init_kwargs)
        
        # Cache if no custom params
        if not init_kwargs:
            cls._instances[name] = tool
        
        return tool
    
    @classmethod
    def list_tools(cls) -> list[str]:
        """List all registered tool names."""
        return list(cls._tools.keys())
    
    @classmethod
    def clear(cls):
        """Clear registry (useful for testing)."""
        cls._tools.clear()
        cls._instances.clear()


# Auto-register existing tools
def initialize_registry():
    """Register all existing tools."""
    from tools.resume_parser import ResumeParserTool
    from tools.job_search import JobSearchTool
    from tools.job_matcher import JobMatchingTool
    from tools.email_drafter import EmailDraftTool
    from tools.file_ops import (
        FileWriteTool, FileReadTool, ListDirTool,
        FileEditTool, CreateFolderTool
    )
    from tools.lead_scraper import LeadScraperTool
    
    ToolRegistry.register_instance("parse_resume", ResumeParserTool)
    ToolRegistry.register_instance("search_jobs", JobSearchTool)
    ToolRegistry.register_instance("scrape_leads", LeadScraperTool)
    ToolRegistry.register_instance("match_jobs", JobMatchingTool)
    ToolRegistry.register_instance("draft_email", EmailDraftTool)
    ToolRegistry.register_instance("write_file", FileWriteTool)
    ToolRegistry.register_instance("read_file", FileReadTool)
    ToolRegistry.register_instance("list_dir", ListDirTool)
    ToolRegistry.register_instance("edit_file", FileEditTool)
    ToolRegistry.register_instance("create_folder", CreateFolderTool)


# Initialize on import
initialize_registry()
