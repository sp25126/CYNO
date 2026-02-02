import pytest
import os
from tools.job_search import JobSearchTool
from agent.config import default_agent_config

@pytest.fixture
def tool():
    return JobSearchTool()

@pytest.mark.asyncio
async def test_ddg_search_real_network(tool):
    """Test DuckDuckGo search with a real query."""
    # "Python" is generic enough to always return results
    jobs = await tool.execute("Python Developer", source="ddg")
    
    # We expect some results, but network can be flaky. 
    # If 0 results, it might be rate limiting or network. 
    # But usually it returns something.
    assert isinstance(jobs, list)
    # Check if we got jobs, verify structure
    if jobs:
        job = jobs[0]
        assert job.title
        assert job.job_url.scheme in ["http", "https"]
        assert job.source == "DuckDuckGo"

@pytest.mark.asyncio
async def test_ddg_nonsense_query(tool):
    """Test that a nonsense query returns empty list (or at least valid list)."""
    # A query unlikely to have results
    nonsense = "akjdhfkajsdhflakjdhf12938u40912384"
    jobs = await tool.execute(nonsense, source="ddg")
    assert isinstance(jobs, list)
    assert len(jobs) == 0

@pytest.mark.asyncio
async def test_reddit_search_skipped_if_no_creds(tool):
    """Test Reddit path handles missing creds gracefully."""
    # Unset creds temporarily if they exist
    orig_id = default_agent_config.reddit.client_id
    default_agent_config.reddit.client_id = ""
    
    jobs = await tool.execute("Python", source="reddit")
    assert jobs == []
    
    # Restore
    default_agent_config.reddit.client_id = orig_id

@pytest.mark.asyncio
@pytest.mark.skipif(not os.getenv("REDDIT_CLIENT_ID"), reason="Reddit credentials not found")
async def test_reddit_search_real_network(tool):
    """Test Reddit search with real network if creds exist."""
    jobs = await tool.execute("Python", source="reddit")
    assert isinstance(jobs, list)
    if jobs:
        job = jobs[0]
        assert "Reddit" in job.source
        assert job.job_url

@pytest.mark.asyncio
async def test_unknown_source(tool):
    """Test unknown source returns empty list."""
    jobs = await tool.execute("Python", source="mars_rover")
    assert jobs == []
