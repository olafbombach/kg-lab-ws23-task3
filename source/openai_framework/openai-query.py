from openai import OpenAI
from api_secrets import API_KEY
client = OpenAI(api_key=API_KEY)
MODEL = "gpt-4"
query="how to search with the DOI on the Core API"

response=client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": query}],
    temperature=0.3
)

print(response)