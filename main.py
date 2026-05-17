import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Create OpenRouter client
client = OpenAI(
    base_url=os.getenv("OPENROUTER_BASE_URL"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# Send first test prompt
response = client.chat.completions.create(
    model=os.getenv("OPENROUTER_MODEL"),
    messages=[
        {
            "role": "user",
            "content": "Reply exactly with: OpenRouter connection successful"
        }
    ]
)

# Print response
print("\n===== AI RESPONSE =====\n")
print(response.choices[0].message.content)