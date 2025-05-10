import json
from .prompt import *
from model import *
import logging
import copy
from openai import OpenAI
from typing import Union

logger = logging.getLogger("llm")

class LLMClient():
    def __init__(self, 
                 model_name: str = "deepseek-chat",
                 api_key: str = None, 
                 base_url: str = "https://api.deepseek.com",
                 temperature: float = 0.7,
                 max_tokens: int = 1000,
                 stream: bool = False,
                 messages: list[MessageInfo] = []):
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.history = self.__convert_messages(messages)
        self.stream = stream
        assert self.api_key, "API key is required"
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)                           

    def __convert_messages(self, messages: list[MessageInfo]) -> list[dict[str, str]]:
        converted_messages = []
        for message in messages:
            converted_messages.append({
                "role": "user",
                "content": message.user_message
            })
            converted_messages.append({
                "role": "assistant",
                "content": message.assistant_message
            })
        return converted_messages

    def generate_response(
        self, 
        prompt: str, 
    ) -> Union[str, list[dict[str, any]]]:
        """
        Generate a response from the LLM using the provided prompt.
        """
        reponse = self.client.chat.completions.create(
            model=self.model_name,
            messages= self.history + [{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=self.stream
        )
        response_content = reponse.choices[0].message.content
        # add the interaction to the message history
        self.history.append({"role": "user", "content": prompt})
        self.history.append({"role": "assistant", "content": response_content})

        # log the interaction
        logger.debug(f"LLM interaction:\n{prompt}\n--------->\n{response_content}\n")

        # TODO: how to handle the stream response ?
        if self.stream:
            return reponse
        else:
            return reponse.choices[0].message.content
        
class ExtractorLLM():
    def __init__(self, 
                 llm_client: LLMClient):
        self.max_retry_count = 3
        self.llm_client = llm_client
        self.extract_prompt = ExtractorPrompt()
        self.retry_prompt = RetryPrompt()
        
    def extract(self, input: str) -> ExtractedInfo:
        prompt = self.extract_prompt.render(
            text=input
        )
        response = self.llm_client.generate_response(prompt)
        extracted = self.check_and_convert(response)
        return extracted
    
    def check_and_convert(self, response: str) -> BaseModel:
        for i in range(self.max_retry_count):
            if (response.startswith("```json")):
                response = response.replace("```json", "").replace("```", "").strip()
            try:
                response_loaded = json.loads(response)
                is_valid = all(key in response_loaded for key in extractedInfoExample.model_dump().keys())
                if is_valid:
                    instance = ExtractedInfo.model_validate(response_loaded)
                    return instance
            except json.JSONDecodeError:
                pass
            prompt = self.retry_prompt.render(extractedInfoExample)
            response = self.llm_client.generate_response(prompt)
        logger.error(f"Failed to parse response after {self.max_retry_count} attempts.")

class NonRAGLLM():
    def __init__(self, 
                 llm_client: LLMClient):
        self.llm_client = llm_client
        self.non_rag_prompt = NonRAGPrompt()

    def chat(self, question: str) -> str:
        prompt = self.non_rag_prompt.render(question=question)
        response = self.llm_client.generate_response(prompt)
        return response
    
class RAGLLM():
    def __init__(self, 
                 llm_client: LLMClient):
        self.llm_client = llm_client
        self.rag_prompt = RAGPrompt()

    def chat(
        self, 
        question: str, 
        context: list[Reference] = None,
    ) -> str:
        prompt = self.rag_prompt.render(context=context, question=question)
        response = self.llm_client.generate_response(prompt)
        return response

class SummarizeLLM():
    def __init__(self, 
                 llm_client: LLMClient):
        self.max_retry_count = 3
        self.llm_client = llm_client
        self.summarize_prompt = SummarizePrompt()
        self.retry_prompt = RetryPrompt()
        
    def summarize(self, messages: list[MessageInfo], old_name: str) -> SummarizeTitle:
        prompt = self.summarize_prompt.render(messages=messages, old_name=old_name)
        response = self.llm_client.generate_response(prompt)
        summarized = self.check_and_convert(response)
        return summarized
    
    def check_and_convert(self, response: str) -> BaseModel:
        for i in range(self.max_retry_count):
            if (response.startswith("```json")):
                response = response.replace("```json", "").replace("```", "").strip()
            try:
                response_loaded = json.loads(response)
                is_valid = all(key in response_loaded for key in summarizeTitleExample.model_dump().keys())
                if is_valid:
                    instance = SummarizeTitle.model_validate(response_loaded)
                    return instance
            except json.JSONDecodeError:
                logger.error(f"JSON decode error: {response}")
                pass
            prompt = self.retry_prompt.render(summarizeTitleExample)
            response = self.llm_client.generate_response(prompt)
        logger.error(f"Failed to parse response after {self.max_retry_count} attempts.")
     
