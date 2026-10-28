
import os
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI

load_dotenv()

llm = ChatMistralAI(
    model=os.getenv("MISTRAL_MODEL", "mistral-small-latest"),
    temperature=0,
)

response = llm.invoke(
    "Explain Multi-Agent AI Research Systems in two sentences."
)

print(response.content)
