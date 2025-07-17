import requests


def ask_llm(prompt, use_openai=False, api_key=None):
    if use_openai:
        import openai
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message["content"]
    else:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama2",
            "prompt": prompt,
            "stream": False
        })
        return response.json().get("response", "").strip()


if __name__ == "__main__":
    example_prompt = "EC2 instance is unreachable and returns no HTTP response on port 80."
    print(ask_llm(example_prompt))
