import os
import requests

def test_api_key(api_key: str) -> bool:
    """Test if the API key is valid"""
    url = "https://api.fireflies.ai/graphql"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    # Simple query to list available transcripts
    query = """
    {
        transcripts(first: 1) {
            edges {
                node {
                    id
                    title
                }
            }
        }
    }
    """
    
    try:
        print("Testing API key...")
        response = requests.post(url, json={"query": query}, headers=headers)
        
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response text: {response.text[:500]}")  # First 500 chars
        
        if response.status_code == 200:
            return True
        return False
    except Exception as e:
        print(f"Error testing API key: {str(e)}")
        return False

# Get API key from environment
api_key = os.getenv('FIREFLIES_API_KEY')
if not api_key:
    print("Error: FIREFLIES_API_KEY environment variable not set")
else:
    print(f"Testing API key (length: {len(api_key)} chars)...")
    if test_api_key(api_key):
        print("API key is valid!")
    else:
        print("API key appears to be invalid")
