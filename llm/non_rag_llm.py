from .prompt import NonRAGPrompt
from .llm_client import LLMClient

class NonRAGLLM():
    """
    A class interacting with a LLM
    """
    def __init__(self, 
                 llm_client: LLMClient):
        self.llm_client = llm_client
        self.prompt = NonRAGPrompt()

    def generate_response(
        self, 
        question: str, 
    ) -> str:
        prompt = self.prompt.render(question=question)
        response = self.llm_client.generate_response(prompt)
        return response