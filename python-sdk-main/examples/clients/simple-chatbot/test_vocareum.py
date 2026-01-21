"""
Test script to verify Vocareum API configuration for simple-chatbot.
"""
from anthropic import Anthropic

# Configuration from main.py
VOCAREUM_API_KEY = "voc-184494821118751213237176904c8dab622c9.37059815"
VOCAREUM_BASE_URL = "https://claude.vocareum.com"

def test_vocareum_connection():
    """Test the Vocareum API connection."""
    print("Testing Vocareum API connection...")
    print(f"API Key: {VOCAREUM_API_KEY[:20]}...")
    print(f"Base URL: {VOCAREUM_BASE_URL}")

    try:
        # Initialize Anthropic client
        client = Anthropic(
            api_key=VOCAREUM_API_KEY,
            base_url=VOCAREUM_BASE_URL
        )

        # Test with a simple message
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=50,
            messages=[{
                "role": "user",
                "content": "Say 'Hello from Vocareum!' and nothing else."
            }]
        )

        # Extract response
        result = response.content[0].text
        print(f"\n✅ SUCCESS: Claude responded with: {result}")
        return True

    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        return False

if __name__ == "__main__":
    test_vocareum_connection()
