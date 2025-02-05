from datetime import datetime, timedelta
import os
import json
import requests
from typing import List, Dict, Optional

class FirefliesTranscriptFetcher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.fireflies.ai/graphql"
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

    def get_transcript_summary(self, transcript_id: str) -> Optional[Dict]:
        """Get summary for a specific transcript by ID"""
        query = """
        query Transcript($transcriptId: String!) {
            transcript(id: $transcriptId) {
                id
                title
                date
                participants {
                    name
                }
                summary {
                    keywords
                    action_items
                    outline
                    shorthand_bullet
                    overview
                    bullet_gist
                    gist
                    short_summary
                }
                sentences {
                    text
                    speaker_name
                }
            }
        }
        """
        
        variables = {
            "transcriptId": transcript_id
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={"query": query, "variables": variables}
            )
            response.raise_for_status()
            
            data = response.json()
            if 'errors' in data:
                print(f"GraphQL errors: {data['errors']}")
                return None
                
            return data['data']['transcript']
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {str(e)}")
            return None

def main():
    # Get API key from environment or .zshrc
    api_key = os.getenv('FIREFLIES_API_KEY')
    if not api_key:
        zshrc_path = os.path.expanduser("~/.zshrc")
        try:
            with open(zshrc_path) as f:
                for line in f:
                    if 'FIREFLIES_API_KEY' in line:
                        api_key = line.split('=')[1].strip().strip("'").strip('"')
                        break
        except Exception as e:
            print(f"Error reading .zshrc: {e}")
    
    if not api_key:
        print("Error: Could not find FIREFLIES_API_KEY")
        return

    # Set up fetcher
    fetcher = FirefliesTranscriptFetcher(api_key)
    
    # Use the provided transcript ID
    transcript_id = "5d9648c3-4bed-402f-acd6-4365b6b5e3bb"
    print(f"Fetching transcript {transcript_id}...")
    
    transcript = fetcher.get_transcript_summary(transcript_id)
    if transcript:
        print("\nTranscript Details:")
        print(f"Title: {transcript['title']}")
        print(f"Date: {transcript['date']}")
        print("Participants:")
        for p in transcript['participants']:
            print(f"- {p['name']}")
        
        print("\nSummary:")
        print(json.dumps(transcript['summary'], indent=2))
        
        # Save full transcript
        save_path = os.path.expanduser("~/Documents/Transcripts")
        os.makedirs(save_path, exist_ok=True)
        
        # Save JSON
        json_path = os.path.join(save_path, f"{transcript_id}.json")
        with open(json_path, 'w') as f:
            json.dump(transcript, f, indent=2)
        print(f"\nSaved full transcript to: {json_path}")
        
        # Save text
        txt_path = os.path.join(save_path, f"{transcript_id}.txt")
        with open(txt_path, 'w') as f:
            f.write(f"Title: {transcript['title']}\n")
            f.write(f"Date: {transcript['date']}\n\n")
            f.write("Participants:\n")
            for p in transcript['participants']:
                f.write(f"- {p['name']}\n")
            f.write("\nTranscript:\n")
            for sentence in transcript['sentences']:
                f.write(f"{sentence['speaker_name']}: {sentence['text']}\n")
        print(f"Saved text transcript to: {txt_path}")
    else:
        print("Failed to fetch transcript")

if __name__ == "__main__":
    main()
