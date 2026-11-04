"""Use our package, then call a web service."""
import requests

from shop.prices import order_total

OLLAMA = "http://127.0.0.1:11434"

print(order_total(120, 2))

response = requests.get(f"{OLLAMA}/api/version", timeout=5)
print(response.status_code, response.json())

response = requests.post(f"{OLLAMA}/api/show", json={"model": "qwen2.5:7b"}, timeout=30)
print(response.status_code, response.json()["details"]["parameter_size"])

response = requests.post(f"{OLLAMA}/api/show", json={"model": "no-such-model"}, timeout=30)
print(response.status_code, response.json())
