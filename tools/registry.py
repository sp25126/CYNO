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
    
    # Core tools
    ToolRegistry.register_instance("parse_resume", ResumeParserTool)
    ToolRegistry.register_instance("search_jobs", JobSearchTool)
    ToolRegistry.register_instance("scrape_leads", LeadScraperTool)
    ToolRegistry.register_instance("match_jobs", JobMatchingTool)
    ToolRegistry.register_instance("write_file", FileWriteTool)
    ToolRegistry.register_instance("read_file", FileReadTool)
    ToolRegistry.register_instance("list_dir", ListDirTool)
    ToolRegistry.register_instance("edit_file", FileEditTool)
    ToolRegistry.register_instance("create_folder", CreateFolderTool)
    
    # Email Tools (Enhanced with personalization)
    try:
        from tools.email_drafter import register_email_tools
        register_email_tools()
    except ImportError:
        from tools.email_drafter import EmailDraftTool
        ToolRegistry.register_instance("draft_email", EmailDraftTool)
    
    # Interview Prep Tools
    try:
        from tools.interview_prep import register_interview_tools
        register_interview_tools()
    except ImportError:
        pass  # Tools not yet created
    
    # Application Enhancement Tools
    try:
        from tools.application_tools import register_application_tools
        register_application_tools()
    except ImportError:
        pass
    
    # Profile Scrapers
    try:
        from tools.profile_scrapers import GitHubProfileScraper, PortfolioScraper
        ToolRegistry.register_instance("github_scraper", GitHubProfileScraper)
        ToolRegistry.register_instance("portfolio_scraper", PortfolioScraper)
    except ImportError:
        pass
    
    # Resume Generator
    try:
        from tools.resume_generator import ResumeGeneratorTool
        ToolRegistry.register_instance("generate_resume", ResumeGeneratorTool)
    except ImportError:
        pass
    
    # Outreach Tools
    try:
        from tools.outreach_tools import register_outreach_tools
        register_outreach_tools()
    except ImportError:
        pass
    
    # Enhanced Parser & LLM Analyzer  
    try:
        from tools.enhanced_parser import EnhancedResumeParser, LLMPoweredAnalyzer
        ToolRegistry.register_instance("enhanced_parser", EnhancedResumeParser)
        ToolRegistry.register_instance("llm_analyzer", LLMPoweredAnalyzer)
    except ImportError:
        pass


    # Discovery & Research Tools
    try:
        from tools.discovery_tools import (
            SalaryEstimatorTool, TechStackDetectorTool,
            InterviewQuestionFinderTool, JobAlertWatcherTool
        )
        ToolRegistry.register_instance("salary_estimator", SalaryEstimatorTool)
        ToolRegistry.register_instance("tech_stack_detector", TechStackDetectorTool)
        ToolRegistry.register_instance("interview_question_finder", InterviewQuestionFinderTool)
        ToolRegistry.register_instance("job_alert_watcher", JobAlertWatcherTool)
    except ImportError:
        pass

    # Analytics Tools
    try:
        from tools.analytics_tools import (
            ApplicationDashboardTool, SuccessPatternAnalyzerTool, 
            OfferComparatorTool
        )
        ToolRegistry.register_instance("application_dashboard", ApplicationDashboardTool)
        ToolRegistry.register_instance("success_pattern_analyzer", SuccessPatternAnalyzerTool)
        ToolRegistry.register_instance("offer_comparator", OfferComparatorTool)
    except ImportError:
        pass

    # Advanced AI Tools
    try:
        from tools.advanced_ai import (
            SalaryNegotiatorTool, WeaknessSpinDoctorTool, PersonalBrandBuilderTool,
            SideProjectIdeaGenTool, JobFitScorerTool, CourseRecommenderTool,
            BlogPostGeneratorTool
        )
        ToolRegistry.register_instance("salary_negotiator", SalaryNegotiatorTool)
        ToolRegistry.register_instance("weakness_spin_doctor", WeaknessSpinDoctorTool)
        ToolRegistry.register_instance("personal_brand_builder", PersonalBrandBuilderTool)
        ToolRegistry.register_instance("side_project_idea_gen", SideProjectIdeaGenTool)
        ToolRegistry.register_instance("job_fit_scorer", JobFitScorerTool)
        ToolRegistry.register_instance("course_recommender", CourseRecommenderTool)
        ToolRegistry.register_instance("blog_post_generator", BlogPostGeneratorTool)
    except ImportError:
        pass

    # Utility Tools
    try:
        from tools.utility_tools import (
            JobDescriptionSummarizerTool, RecruiterFinderTool, DocumentVaultTool,
            ReminderBotTool, CalendarSyncTool
        )
        ToolRegistry.register_instance("job_description_summarizer", JobDescriptionSummarizerTool)
        ToolRegistry.register_instance("recruiter_finder", RecruiterFinderTool)
        ToolRegistry.register_instance("document_vault", DocumentVaultTool)
        ToolRegistry.register_instance("reminder_bot", ReminderBotTool)
        ToolRegistry.register_instance("calendar_sync", CalendarSyncTool)
    except ImportError:
        pass


# Initialize on import
initialize_registry()

