from .prompt import RAGPrompt
from .llm_client import LLMClient
from typing import List, Dict

class RAGLLM():
    """
    A class interacting with a LLM with retrieval context.
    """

    def __init__(self, 
                 llm_client: LLMClient):
        self.llm_client = llm_client
        self.prompt = RAGPrompt()

    def __format_context(self, context: List[Dict[str, str]]) -> str:
        formatted_context = ""
        for item in context:
            formatted_context += "这是名为{}的参考资料：\n".format(item.get("description"))
            formatted_context += item.get("content") + "\n"
            formatted_context += "\n"
        return formatted_context

    def generate_response(
        self, 
        question: str, 
        context: List[Dict[str, str]] = None,
        topic_name: str = "MineCraft Mod"
    ) -> str:
        formatted_context = self.__format_context(context or self.context)
        prompt = self.prompt.render(context_content=formatted_context, question=question, topic_name=topic_name)
        response = self.llm_client.generate_response(prompt)
        return response