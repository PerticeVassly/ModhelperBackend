import json
from .llm_client import LLMClient
from config import settings
from .prompt import ExtractorPrompt, RAGPrompt, RetryPrompt

class ExtractorLLM():
    """
    LLM to extract the key words from the user input."""
    def __init__(self, 
                 llm_client: LLMClient):
        self.max_retry_count = 3
        self.llm_client = llm_client
        self.extract_prompt = ExtractorPrompt()
        self.retry_prompt = RetryPrompt()
        
    def extract(self,
                 input_text: str,
                 key_words: list[str],
                 topic_name: str) -> dict:
        prompt = self.extract_prompt.render(
            key_words=key_words,
            topic_name=topic_name,
            input_text=input_text
        )
        response = self.llm_client.generate_response(prompt)
        checked_response = self.check_response_format(response)
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
                if (settings.DEBUG):
                    print("Response format is incorrect, retrying...")
            prompt = self.retry_prompt.render(key_words=key_words)
            response = self.llm_client.generate_response(prompt)
        raise ValueError("LLM can't generate the formated response. Please check whether the LLM you choose is not stable or your prompt is not clear enough")
