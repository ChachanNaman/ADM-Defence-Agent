from openai import OpenAI

from app.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_PROVIDER


def main() -> None:
    client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": "Reply with exactly: OK"}],
    )
    print(f"provider: {LLM_PROVIDER}")
    print(f"model: {LLM_MODEL}")
    print(f"response: {response.choices[0].message.content}")


if __name__ == "__main__":
    main()
