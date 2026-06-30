from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

print("SDK loaded")
print("Key starts with:", os.getenv("GEMINI_API_KEY")[:4])

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say hello."
)

print(response.text)