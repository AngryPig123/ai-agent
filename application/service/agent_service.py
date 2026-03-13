from domain.port.llm_port import LLMPort


class AgentService:
    def __init__(self, llm: LLMPort):
        self.llm = llm

    def ask(self, text: str) -> str:
        return self.llm.generate(text)
