import json
import openai
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

app = FastAPI()

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

class PersonaChat:
    def __init__(self, persona_file: str):
        self.load_persona(persona_file)
        self.conversation_history = []

    def load_persona(self, persona_file: str):
        """Load the persona profile"""
        with open(persona_file, 'r') as f:
            self.persona = json.load(f)

    def generate_system_prompt(self) -> str:
        """Create a system prompt based on the persona"""
        return f"""You are {self.persona['name']}.
        Your writing style is: {self.persona['writing_style']['style_analysis']}
        You typically talk about: {', '.join(self.persona['topics'])}
        
        Important guidelines:
        1. Respond in your characteristic style while maintaining consistency with your known interests and tone
        2. Use your writing patterns and common phrases naturally
        3. Stay true to the topics and expertise shown in your tweets
        4. If asked about something outside your knowledge base, acknowledge it honestly
        5. Maintain the same personality throughout the conversation"""

    async def get_response(self, message: str) -> str:
        """Generate a response in the persona's style"""
        # Add the new message to conversation history
        self.conversation_history.append({"role": "user", "content": message})

        # Prepare the messages for the API call
        messages = [
            {"role": "system", "content": self.generate_system_prompt()}
        ] + self.conversation_history[-5:]  # Keep last 5 messages for context

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )

        # Add the response to conversation history
        ai_response = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": ai_response})

        return ai_response

# Global persona chat instance
persona_chat = None

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage):
    if not persona_chat:
        raise HTTPException(status_code=400, detail="Persona not loaded")
    response = await persona_chat.get_response(message.message)
    return ChatResponse(response=response)

@app.post("/load_persona/{name}")
async def load_persona_endpoint(name: str):
    persona_file = f'profiles/{name}_persona.json'
    if not os.path.exists(persona_file):
        raise HTTPException(status_code=404, detail="Persona not found")
    global persona_chat
    persona_chat = PersonaChat(persona_file)
    return {"status": "success", "message": f"Loaded persona for {name}"}

@app.get("/available_personas")
def list_personas():
    """List all available persona profiles"""
    if not os.path.exists('profiles'):
        return {"personas": []}
    personas = [f.replace('_persona.json', '') 
               for f in os.listdir('profiles') 
               if f.endswith('_persona.json')]
    return {"personas": personas}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)