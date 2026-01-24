import pytest
import asyncio
from agent.orchestrator import JobAgentOrchestrator
from agent.state import AgentState
from agent.nodes import routing_node
from scripts.infra_manager import start_ollama

# Ensure Ollama is up (No Mocks allowed)
if not start_ollama():
    pytest.skip("Ollama not running. Skipping integration tests.", allow_module_level=True)

@pytest.fixture
def orchestrator():
    return JobAgentOrchestrator()

@pytest.mark.asyncio
async def test_workflow_resume_upload_flow(orchestrator):
    """
    Scenario: User uploads resume text.
    Expectation: Parse -> Ask for missing info (since location/exp is missing)
    """
    resume_text = """
    SAUMYA PATEL
    Bopal, Ahmedabad, India | +91 8866553976 | saumyavishwam@gmail.com
    SUMMARY
    Creative AI & Full-Stack Developer and second-year B.Tech Computer Science student.
    Skilled in JavaScript, C, Python, and modern frameworks.
    """
    
    result = await orchestrator.run(f"Here is my resume: {resume_text}", "test_session_1")
    
    # Assertions
    assert result.get("parsed_resume") is not None, "Resume should be parsed"
    skills = [s.lower() for s in result["parsed_resume"].parsed_skills]
    assert "python" in skills or "javascript" in skills, "Should extract Python/JS"
    
    # Updated Expectation: Agent might search immediately using extracted skills
    last_msg = result['messages'][-1]['content'].lower()
    valid_outcomes = ["experience", "jobs", "found", "match", "search"]
    assert any(x in last_msg for x in valid_outcomes), f"Agent should ask for info or show results, but said: {last_msg}"

@pytest.mark.asyncio
async def test_workflow_direct_search_flow(orchestrator):
    """
    Scenario: User asks for jobs directly.
    Expectation: Skip Parse -> Direct Search -> Respond with results
    """
    query = "Find me Python jobs in London"
    result = await orchestrator.run(query, "test_session_2")
    
    # Logic cleans the query, so checking containment
    assert "python" in result.get("search_query", "").lower(), "Query should contain keywords"
    assert result.get("jobs_found") is not None, "Should have a jobs list"
    
    last_msg = result['messages'][-1]['content'].lower()
    # Depending on web results, it might find jobs or not
    if result.get("jobs_found"):
        assert "found" in last_msg or "match" in last_msg, f"Response should mention jobs. Got: {last_msg}"
    else:
        assert "couldn't find" in last_msg or "no jobs" in last_msg, f"Response should handle 0 results. Got: {last_msg}"


@pytest.mark.asyncio
async def test_error_recovery_no_results(orchestrator):
    """
    Scenario: Nonsense query.
    Expectation: Search returns empty -> Agent apologizes.
    """
    nonsense_query = "Find me jobs for Cobalt_60_Miner_on_Mars_12345_XYZ"
    result = await orchestrator.run(nonsense_query, "test_session_3")
    
    jobs = result.get("jobs_found", [])
    assert len(jobs) == 0, "Should find 0 jobs"
    
    last_msg = result['messages'][-1]['content'].lower()
    failure_indicators = ["couldn't find", "sorry", "no jobs"]
    assert any(x in last_msg for x in failure_indicators), f"Response should verify failure. Got: {last_msg}"

@pytest.mark.asyncio
async def test_heuristic_routing_logic():
    """
    Scenario: Test the new heuristic-based routing_node in isolation.
    """
    # Case A: User asks to find a job
    state_a = {"messages": [{"role": "user", "content": "Show me jobs for a python developer"}]}
    decision_a = await routing_node(state_a)
    assert decision_a["next_step"] == "search", "Should route to search"
    # Logic cleans "Show me jobs for" -> checks keywords
    assert "python" in decision_a["search_query"], "Query should capture key terms"

    # Case B: User uploads a resume
    state_b = {"messages": [{"role": "user", "content": "Here is my resume..."}]}
    decision_b = await routing_node(state_b)
    assert decision_b["next_step"] == "parse_resume", "Should route to parse_resume"

    # Case C: User just says hello
    state_c = {"messages": [{"role": "user", "content": "Hello there"}]}
    decision_c = await routing_node(state_c)
    assert decision_c["next_step"] == "respond", "Should route to respond for conversation"
