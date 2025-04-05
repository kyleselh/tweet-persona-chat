import json
import os
from typing import Dict, List
import openai
from dotenv import load_dotenv
from datetime import datetime
from pydantic import BaseModel

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

class Tweet(BaseModel):
    text: str
    timestamp: str = None

class Profile(BaseModel):
    name: str
    tweets: List[Tweet]
    created_at: str

class ProfileGenerator:
    def __init__(self, name: str):
        self.name = name

    def create_profile_from_tweets(self, tweets: List[str]) -> Dict:
        """Create a profile from a list of tweets"""
        # Convert tweets to Tweet objects
        tweet_objects = [
            Tweet(text=tweet, timestamp=datetime.now().isoformat())
            for tweet in tweets
        ]

        # Create initial profile
        profile = Profile(
            name=self.name,
            tweets=tweet_objects,
            created_at=datetime.now().isoformat()
        )

        # Analyze writing style
        style_analysis = self.analyze_writing_style(tweets)
        
        # Extract topics
        topics = self.extract_topics(tweets)

        # Create final persona
        persona = {
            'name': self.name,
            'tweets': [tweet.dict() for tweet in profile.tweets],
            'writing_style': style_analysis,
            'topics': topics,
            'interaction_guidelines': {
                'tone': style_analysis['style_analysis'],
                'knowledge_base': topics
            },
            'created_at': profile.created_at
        }

        # Save persona
        self.save_persona(persona)
        return persona

    def analyze_writing_style(self, tweets: List[str]) -> Dict:
        """Analyze the writing style from tweets"""
        analysis_prompt = f"Analyze these tweets and describe the writing style, common phrases, and tone:\n{tweets[:10]}"

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": """Analyze the writing style, tone, and patterns in these tweets. Focus on:
                    1. Tone (formal, casual, humorous, etc.)
                    2. Common phrases or expressions
                    3. Writing patterns (sentence structure, punctuation usage)
                    4. Unique stylistic elements"""
            }, {
                "role": "user",
                "content": analysis_prompt
            }]
        )

        return {
            'style_analysis': response.choices[0].message.content,
            'sample_tweets': tweets[:10]
        }

    def extract_topics(self, tweets: List[str]) -> List[str]:
        """Extract common topics from tweets"""
        tweets_text = '\n'.join(tweets)
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": "Extract the main topics, interests, and areas of expertise from these tweets. "
                           "Return them as a list of specific topics."
            }, {
                "role": "user",
                "content": tweets_text
            }]
        )

        # Parse the response into a list of topics
        topics = response.choices[0].message.content.split('\n')
        return [topic.strip('- ') for topic in topics if topic.strip('- ')]

    def save_persona(self, persona: Dict):
        """Save the persona to a JSON file"""
        os.makedirs('profiles', exist_ok=True)
        output_path = f'profiles/{self.name}_persona.json'
        
        with open(output_path, 'w') as f:
            json.dump(persona, f, indent=2)
        print(f"Persona saved to {output_path}")

def load_tweets_from_file(file_path: str) -> List[str]:
    """Load tweets from a text file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', required=True, help='Name for the persona')
    parser.add_argument('--tweets_file', required=True, help='File containing tweets, one per line')
    args = parser.parse_args()

    tweets = load_tweets_from_file(args.tweets_file)
    generator = ProfileGenerator(args.name)
    generator.create_profile_from_tweets(tweets)