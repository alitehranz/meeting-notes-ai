import os
from dotenv import load_dotenv
import json
import re
import requests

load_dotenv()

class MeetingAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def analyze_meeting_notes(self, raw_notes: str) -> dict:
        """Extract structured data from raw meeting notes"""
        
        prompt = f"""
You are a meeting notes analyzer. Extract the following from these meeting notes:

1. ACTION ITEMS: Tasks that need to be done, who is responsible, and any deadlines
   Format: [{{"task": "...", "assigned_to": "...", "deadline": "..."}}]

2. DECISIONS: Key decisions that were made
   Format: ["Decision 1", "Decision 2", ...]

3. KEY POINTS: Important discussion topics or takeaways
   Format: ["Point 1", "Point 2", ...]

4. SUMMARY: A brief 2-3 sentence summary of the meeting

Meeting Notes:
{raw_notes}

Return ONLY valid JSON in this exact format:
{{
  "action_items": [{{"task": "...", "assigned_to": "...", "deadline": "..."}}],
  "decisions": ["..."],
  "key_points": ["..."],
  "summary": "..."
}}

If any section has no items, return an empty array [].
"""
        
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "anthropic/claude-3-haiku",
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            
            result = response.json()
            print(f"OpenRouter Response: {result}")
            result_text = result["choices"][0]["message"]["content"].strip()
            
            # Clean up response
            result_text = re.sub(r'^```json\s*', '', result_text)
            result_text = re.sub(r'\s*```$', '', result_text)
            result_text = result_text.strip()
            
            # Parse JSON
            parsed = json.loads(result_text)
            
            return {
                "action_items": parsed.get("action_items", []),
                "decisions": parsed.get("decisions", []),
                "key_points": parsed.get("key_points", []),
                "summary": parsed.get("summary", "No summary available")
            }
            
        except Exception as e:
            print(f"AI Analysis Error: {e}")
            return self._get_fallback_response()
    
    def _get_fallback_response(self):
        """Return safe fallback if AI fails"""
        return {
            "action_items": [],
            "decisions": [],
            "key_points": [],
            "summary": "Unable to analyze meeting notes. Please try again."
        }
