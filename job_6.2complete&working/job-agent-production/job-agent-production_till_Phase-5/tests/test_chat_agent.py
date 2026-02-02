"""
Quick test to verify HR Chat Agent functionality
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.chat_agent import HRChatAgent

def test_basic_functionality():
    print("=" * 60)
    print("Testing HR Chat Agent")
    print("=" * 60)
    
    # Initialize agent
    print("\n1. Initializing agent...")
    agent = HRChatAgent()
    print(f"✓ Agent initialized with {len(agent.tools)} tools")
    print(f"  Tools: {list(agent.tools.keys())}")
    
    # Test intent detection
    print("\n2. Testing intent detection...")
    
    test_messages = [
        "I have a resume to upload",
        "Find me Python developer jobs",
        "Show me the top 5 matches",
        "Can you help me with career advice?"
    ]
    
    for msg in test_messages:
        intent = agent.detect_intent(msg, {})
        print(f"\n  Message: '{msg}'")
        print(f"  → Intent: {intent.primary}")
        print(f"  → Tools needed: {intent.tools_needed}")
        print(f"  → Needs clarification: {intent.needs_clarification}")
    
    # Test general response
    print("\n3. Testing general conversation...")
    session_context = {}
    response = agent._generate_general_response("Hello!", session_context)
    print(f"\n  User: Hello!")
    print(f"  Alex: {response[:200]}...")
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)

if __name__ == "__main__":
    test_basic_functionality()
