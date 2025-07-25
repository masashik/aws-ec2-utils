import requests
import time


def ask_llm_for_action(prompt, use_openai=False, api_key=None):

    instruction = "Just return the answer as restart or ignore only based on the provided prompt."
    OLLAMA_API_URL = "http://localhost:11434/api/generate"

    print("=======This is the prompt provided=======================")
    print(prompt)
    print("=========================================================")

    if use_openai:
        import openai
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message["content"]
    else:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.1",
                "prompt": f"{prompt}\n\n{instruction}",
                "stream": False
            },
            timeout=60.0
        )
        return response.json().get("response", "").strip()


if __name__ == "__main__":
    example_prompt = "EC2 instance is unreachable and returns no HTTP response on port 80."
    print(ask_llm(example_prompt))
