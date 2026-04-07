# test_ollama.py
import requests

def test_ollama():
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi3",
                "prompt": "Say 'Hello Healthcare'",
                "stream": False
            }
        )
        if response.status_code == 200:
            print("✅ Ollama working!")
            print(f"Response: {response.json()['response']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("\n💡 Start Ollama first:")
        print("   ollama serve")

if __name__ == "__main__":
    test_ollama()