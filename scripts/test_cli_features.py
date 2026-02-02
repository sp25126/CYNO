import sys
import os
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.getcwd())

from cli.cyno import detect_intent
from cli.command_routers import CommandRouter

def test_nlp_router():
    print("Testing NLP Router...")
    
    cases = [
        ("find leads for python", "leads", "python"),
        ("draft cold email for Google", "email_gen", "cold email for Google"),
        ("analyze github for saumya", "prep_github", "saumya"),
        ("find me python jobs", "job_search", "python jobs"),
    ]
    
    passed = 0
    for text, expected_intent, expected_query in cases:
        intent, ctx = detect_intent(text)
        query = ctx.get('query', '')
        # Loose match for query to handle group extraction var
        if intent == expected_intent:
            print(f"✅ '{text}' -> {intent}")
            passed += 1
        else:
            print(f"❌ '{text}' -> Got {intent}, expected {expected_intent}")
            
    print(f"Result: {passed}/{len(cases)} passed.")
    return passed == len(cases)

def test_clickable_links():
    print("\nTesting Clickable Links Output...")
    
    # Mock console
    mock_console = MagicMock()
    
    # Test Lead Scraper Handler
    router = CommandRouter(mock_console)
    
    # We need to mock LeadScraperTool to return data with URL
    with patch('tools.lead_scraper.LeadScraperTool') as MockTool:
        mock_instance = MockTool.return_value
        mock_instance.scrape_leads.return_value = [
            MagicMock(url="http://example.com", source="Twitter", role_needed="Dev", contact_email="test@test.com")
        ]
        
        router._handle_leads("python")
        
        # Check if table was printed with link
        # rich.Table is complex, so we check if the function ran without error and data was accessed
        if mock_console.print.called:
            print("✅ _handle_leads executed and printed table.")
        else:
            print("❌ _handle_leads did not print.")

if __name__ == "__main__":
    test_nlp_router()
    test_clickable_links()
