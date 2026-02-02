import sys
import os
try:
    print(f"✅ Python {sys.version.split()[0]}")
    import pydantic
    print(f"✅ pydantic {pydantic.__version__}")
    import langgraph
    print(f"✅ langgraph imported")
    import langchain
    print(f"✅ langchain {langchain.__version__}")
    import structlog
    print(f"✅ structlog imported")
    import requests
    print(f"✅ requests {requests.__version__}")
    
    from dotenv import load_dotenv
    if load_dotenv():
        print("✅ .env loaded")
        if "OLLAMA_BASE_URL" in os.environ:
             print(f"   OLLAMA_BASE_URL found: {os.environ['OLLAMA_BASE_URL']}")
        else:
             print("   ⚠️ OLLAMA_BASE_URL not set in .env")
    else:
        print("❌ .env not found or empty")

except ImportError as e:
    print(f"❌ Import Failed: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
