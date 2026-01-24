import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from agent.chat_agent import HRChatAgent
    print("Agent import successful")
    agent = HRChatAgent()
    print("Agent init successful")
except Exception as e:
    print(f"Agent failed: {e}")
    import traceback
    traceback.print_exc()
