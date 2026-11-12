from src.artificial_intelligence.ollama_client import OllamaClient


client = OllamaClient()

response = client.generate(
    "You are an assistant for a 3D printing application. "
    "Explain briefly what an STL file is."
)

print(response)