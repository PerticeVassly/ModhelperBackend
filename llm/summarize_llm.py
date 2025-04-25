import json
from .llm_client import LLMClient
from .prompt import SummarizePrompt, RetryPrompt
from model import MessageInfo
import logging

logger = logging.getLogger("llm")

class SummarizeLLM():
    """
    LLM to extract the key words from the user input."""
    def __init__(self, 
                 llm_client: LLMClient):
        self.max_retry_count = 3
        self.llm_client = llm_client
        self.summarize_prompt = SummarizePrompt()
        self.retry_prompt = RetryPrompt()
        
    def summarize(self,
                 messages: list[MessageInfo], old_name: str) -> dict:
        prompt = self.summarize_prompt.render(messages=messages, old_name=old_name)
        response = self.llm_client.generate_response(prompt)
        checked_response = self.check_response_format(response, ["title"])
        return json.loads(checked_response)
    
    def check_response_format(self, response: str, key_words : list[str]) -> dict:
        for i in range(self.max_retry_count):
            if (response.startswith("```json")):
                response = response.replace("```json", "").replace("```", "").strip()
            try:
                response_loaded = json.loads(response)
                if isinstance(response_loaded, dict) and all(key in response_loaded for key in key_words):
                    return response
            except json.JSONDecodeError:
                pass
            prompt = self.retry_prompt.render(key_words=key_words)
            response = self.llm_client.generate_response(prompt)
        logger.error(f"Failed to parse response after {self.max_retry_count} attempts.")