from adapter.llm.ollama_adapter import OllamaLLMAdapter
from application.service.agent_service import AgentService


def main():
    llm = OllamaLLMAdapter(
        model="qwen2.5:7b"
    )

    service = AgentService(llm)

    result = service.ask(
        "DDD가 무엇인지 설명해줘"
    )

    print(result)


if __name__ == "__main__":
    main()
