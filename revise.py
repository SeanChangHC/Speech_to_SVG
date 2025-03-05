import requests
import sys

# Define constants
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:0.5b"
PROMPT_TEMPLATE = "Please check and fix ONLY the grammar in the following text. Do NOT change any words or rephrase the content. Keep the original meaning and vocabulary intact. Only correct grammatical errors. Return ONLY the corrected text without any explanations, prefixes, or phrases like 'In this revised version...': '{}'."

def correct_and_rephrase(text):
    payload = {
        "model": MODEL_NAME,
        "prompt": PROMPT_TEMPLATE.format(text),
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()  # Will raise an exception for 4XX/5XX responses
        result = response.json().get("response", "").strip()
        
        # Post-processing to remove explanatory prefixes if they still appear
        prefixes = [
            "here is the corrected text:",
            "corrected text:",
            "in this revised version",
            "the corrected sentence is:",
            "grammar correction:"
        ]
        
        result_lower = result.lower()
        for prefix in prefixes:
            if result_lower.startswith(prefix):
                result = result[len(prefix):].strip()
                
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Ollama: {e}")
        print("Make sure Ollama is running with: sudo systemctl start ollama")
        return None

def save_transcript(original, revised, filename="revised_transcripts.txt"):
    with open(filename, "a") as file:
        file.write(f"Original: {original}\nRevised: {revised}\n\n")

# Example usage
if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Use command line input if provided
        transcript = " ".join(sys.argv[1:])
    else:
        # Use the example if no input provided
        transcript = "I were good at many dogs at home."
    
    print(f"Original: {transcript}")
    revised_text = correct_and_rephrase(transcript)
    if revised_text:
        print(f"Revised: {revised_text}")
        save_transcript(transcript, revised_text)
