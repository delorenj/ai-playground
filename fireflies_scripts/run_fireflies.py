from fireflies_fetcher import FirefliesTranscriptFetcher
import os
from pathlib import Path
import re

def get_api_key_from_zshrc():
    zshrc_path = Path.home() / ".zshrc"
    try:
        with open(zshrc_path, 'r') as f:
            content = f.read()
            match = re.search(r"export FIREFLIES_API_KEY=['\"]([^'\"]+)['\"]", content)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"Error reading .zshrc: {e}")
    return None

def main():
    # Try getting API key from environment first
    api_key = os.getenv('FIREFLIES_API_KEY')
    
    # If not in environment, try reading from .zshrc
    if not api_key:
        api_key = get_api_key_from_zshrc()
        
    if not api_key:
        print("Error: Could not find FIREFLIES_API_KEY in environment or .zshrc")
        return

    # Set the base path where transcripts will be saved
    base_path = str(Path.home() / "Documents")
    
    try:
        # Initialize the fetcher
        fetcher = FirefliesTranscriptFetcher(api_key)
        
        # Search for "General concepts" transcripts
        print("Fetching 'General concepts' transcripts...")
        transcripts = fetcher.search_transcripts("General concepts")
        
        # Save each transcript
        for transcript in transcripts:
            print(f"\nSaving transcript: {transcript['title']}")
            fetcher.save_transcript(transcript, base_path)
        
        if transcripts:
            print(f"\nSuccess! Saved {len(transcripts)} transcripts to:")
            print(f"{base_path}/RepRally/Transcripts/")
        else:
            print("\nNo 'General concepts' transcripts found in the last 30 days.")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
