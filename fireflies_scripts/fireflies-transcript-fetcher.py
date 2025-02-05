from datetime import datetime, timedelta
import os
import json
import requests
from typing import List, Dict

class FirefliesTranscriptFetcher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = \"https://api.fireflies.ai/graphql\"
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

    def search_transcripts(self, query: str, days: int = 10) -> List[Dict]:
        \"\"\"Search for transcripts containing specific text within the last N days\"\"\"
        from_date = (datetime.now() - timedelta(days=days)).strftime(\"%Y-%m-%dT%H:%M:%S.000Z\")
        to_date = datetime.now().strftime(\"%Y-%m-%dT%H:%M:%S.000Z\")
        
        query_str = \"\"\"
        query SearchTranscripts($fromDate: String!, $toDate: String!) {
            transcripts(fromDate: $fromDate, toDate: $toDate) {
                id
                title
                dateString
                transcript_url
                summary {
                    keywords
                    outline
                    short_summary
                }
                sentences {
                    text
                    speaker_name
                }
            }
        }
        \"\"\"
        
        variables = {
            \"fromDate\": from_date,
            \"toDate\": to_date
        }
        
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json={\"query\": query_str, \"variables\": variables}
        )
        
        if response.status_code != 200:
            raise Exception(f\"Query failed: {response.text}\")
            
        transcripts = response.json()['data']['transcripts']
        return [t for t in transcripts if query.lower() in t['title'].lower()]

    def save_transcript(self, transcript: Dict, base_path: str):
        \"\"\"Save transcript data in CSV and JSON formats\"\"\"
        # Create directory if it doesn't exist
        dir_path = os.path.join(base_path, \"RepRally\", \"Transcripts\")
        os.makedirs(dir_path, exist_ok=True)
        
        # Save JSON summary
        summary_path = os.path.join(dir_path, f\"{transcript['id']}_summary.json\")
        with open(summary_path, 'w') as f:
            json.dump(transcript['summary'], f, indent=2)
            
        # Save CSV transcript
        csv_path = os.path.join(dir_path, f\"{transcript['id']}_transcript.csv\")
        with open(csv_path, 'w') as f:
            f.write(\"Speaker,Text\
\")  # CSV header
            for sentence in transcript['sentences']:
                speaker = sentence['speaker_name'].replace('\"', '\"\"')
                text = sentence['text'].replace('\"', '\"\"')
                f.write(f'\"{speaker}\",\"{text}\"\
')

    def fetch_office_tour_transcripts(self, api_key: str, obsidian_path: str) -> int:
        transcripts = self.search_transcripts(\"office tour\")
        for transcript in transcripts:
            self.save_transcript(transcript, obsidian_path)
            print(f\"Saved transcript: {transcript['title']}\")
        return len(transcripts)
`
}
