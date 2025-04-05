# Tweet Persona Chat

A tool that creates AI chat personas based on provided tweets. Simply input a collection of tweets, and the system will create an interactive chatbot that mimics the writing style and personality of the tweet author.

## Features

- Create JSON profiles from provided tweets
- Analyze writing style and personality
- Interactive chat interface that responds in the user's style

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

## Usage

### 1. Create a Profile from Tweets

Create a text file (e.g., `tweets.txt`) with the tweets, one per line:
```
This is tweet number 1
Here's another tweet with #hashtags
Responding to interesting topics
```

Then create a profile:
```bash
python create_profile.py --name "PersonaName" --tweets_file tweets.txt
```

This will create a JSON profile in the `profiles` directory.

### 2. Start the Chat Server

```bash
python chat.py
```

### 3. Interact with the Chat API

The chat server provides these endpoints:

- `POST /load_persona/{name}` - Load a specific persona
- `POST /chat` - Send a message and get a response
- `GET /available_personas` - List available personas

Example using curl:
```bash
# Load a persona
curl -X POST "http://localhost:8000/load_persona/PersonaName"

# Chat with the persona
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello! How are you?"}'
```

## How it Works

1. **Profile Creation**:
   - Takes a list of tweets as input
   - Analyzes writing style, tone, and common phrases
   - Identifies main topics and interests
   - Creates a JSON profile with all this information

2. **Chat Interface**:
   - Uses the profile to generate responses in the same style
   - Maintains conversation context
   - Stays true to the persona's topics and expertise

## License

MIT