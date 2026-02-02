import asyncio
import structlog
from agent.graph import build_agent_graph
from agent.state import AgentState

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)

class AgentScenarioRunner:
    def __init__(self):
        self.graph = build_agent_graph()

    async def run_scenario(self, name: str, user_input: str, initial_resume=None):
        print(f"\n=== Running Scenario: {name} ===")
        print(f"User Input: {user_input.strip()[:100]}...")
        
        initial_state = {
            "messages": [{"role": "user", "content": user_input}],
            "parsed_resume": initial_resume,
            "search_query": "",
            "jobs_found": [],
            "matched_jobs": [],
            "next_step": ""
        }
        
        try:
            final_state = await self.graph.ainvoke(initial_state, config={"recursion_limit": 15})
            self._print_results(final_state)
            return True
        except Exception as e:
            print(f"Scenario failed: {e}")
            return False

    def _print_results(self, state):
        msgs = state.get("messages", [])
        last_msg = msgs[-1]['content'] if msgs else "No response"
        print(f"[>] Final Response: {last_msg[:100]}...")
        
        jobs = state.get("jobs_found", [])
        matches = state.get("matched_jobs", [])
        
        print(f"    - Jobs Found: {len(jobs)}")
        print(f"    - Matches: {len(matches)}")
        
        if matches:
            top = matches[0]
            print(f"    - Top Match: {top[0].title} (Score: {top[1]:.2f})")

async def run_full_suite():
    runner = AgentScenarioRunner()
    
    # Scene A: User provides resume text + intent (Standard)
    txt_resume = "I am a Senior Python Developer with Django experience. Location: Remote."
    await runner.run_scenario("A: Resume + Jobs", txt_resume + " Find me jobs.")
    
    # Scene B: User asks for jobs without resume (Agent should handle gracefully, e.g. ask or generic search)
    # The router might default to search or ask. Our prompt defaults to generic search if no resume.
    await runner.run_scenario("B: Jobs w/o Resume", "Find me generic Python jobs.")
    
    # Scene C: Error/Retry (Empty results simulation usually requires mocking, but we'll try a weird query)
    await runner.run_scenario("C: No Results Expectation", "Find me jobs for Cobalt_60_Miner_on_Mars_12345")

if __name__ == "__main__":
    asyncio.run(run_full_suite())
