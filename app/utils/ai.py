from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client with API key
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set")

client = Groq(api_key=api_key)

def generate_ai_completion(prompt: str, system_message: str = "Eres un experto en diseño de emails. Genera un HTML de email profesional y responsivo según el siguiente prompt. Devuelve solamente el HTML sin etiquetas adicionales ni explicaciones. hazlo bonito y con una gama de colores azules y verdes."):
    """
    Generate completion using Groq AI
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=False
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error generating AI completion: {str(e)}")
        return None