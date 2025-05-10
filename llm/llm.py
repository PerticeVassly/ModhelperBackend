import json
from .prompt import *
from model import *
import logging
import copy
from openai import OpenAI
from typing import Union
from pydantic import ValidationError
from typing import Type
from abc import ABC, abstractmethod

logger = logging.getLogger("llm")

class LLMClient():
    def __init__(self, 
                 model_name: str = "deepseek-chat",
                 api_key: str = None, 
                 base_url: str = "https://api.deepseek.com",
                 termperature: float = 0.7,
                 max_tokens: int = 1000,
                 stream: bool = False,
                 messages: list[dict[str, str]] = []):
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self.temperature = termperature
        self.max_tokens = max_tokens
        self.messages = copy.deepcopy(messages)
        self.stream = stream
        assert self.api_key, "API key is required"
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)                           

    def generate_response(
        self, 
        prompt: str, 
    ) -> Union[str, list[dict[str, any]]]:
        """
        Generate a response from the LLM using the provided prompt.
        """
        reponse = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=self.stream
        )
        response_content = reponse.choices[0].message.content
        # add the interaction to the message history
        self.messages.append({"role": "user", "content": prompt})
        self.messages.append({"role": "assistant", "content": response_content})

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
        
    def extract(self, input_text: str) -> ExtractedInfo:
        prompt = self.extract_prompt.render(
            input_text=input_text
        )
        response = self.llm_client.generate_response(prompt)
        checked_response = self.check_response_format(response)
        return checked_response
    
    def check_response_format(self, response: str) -> BaseModel:
        for i in range(self.max_retry_count):
            if (response.startswith("```json")):
                response = response.replace("```json", "").replace("```", "").strip()
            try:
                response_loaded = json.loads(response)
                # Check if all keys are present in the response
                is_valid = all(key in response_loaded for key in extractedInfoExample.model_dump().keys())
                if is_valid:
                    # Validate the response against the example
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
        self.prompt = NonRAGPrompt()

    def generate_response(
        self, 
        question: str, 
    ) -> str:
        prompt = self.prompt.render(question=question)
        response = self.llm_client.generate_response(prompt)
        return response
    
class RAGLLM():
    def __init__(self, 
                 llm_client: LLMClient):
        self.llm_client = llm_client
        self.prompt = RAGPrompt()

    def generate_response(
        self, 
        question: str, 
        context: list[Reference] = None,
    ) -> str:
        prompt = self.prompt.render(context_content=context, question=question)
        response = self.llm_client.generate_response(prompt)
        return response

class SummarizeLLM():
    def __init__(self, 
                 llm_client: LLMClient):
        self.max_retry_count = 3
        self.llm_client = llm_client
        self.summarize_prompt = SummarizePrompt()
        self.retry_prompt = RetryPrompt()
        
    def summarize(self, messages: list[MessageInfo], old_name: str) -> dict:
        prompt = self.summarize_prompt.render(messages=messages, old_name=old_name)
        response = self.llm_client.generate_response(prompt)
        checked_response = self.check_response_format(response)
        return checked_response
    
    def check_response_format(self, response: str) -> BaseModel:
        for i in range(self.max_retry_count):
            if (response.startswith("```json")):
                response = response.replace("```json", "").replace("```", "").strip()
            try:
                response_loaded = json.loads(response)
                # Check if all keys are present in the response
                is_valid = all(key in response_loaded for key in summarizeTitleExample.model_dump().keys())
                if is_valid:
                    # Validate the response against the example
                    instance = SummarizeTitle.model_validate(response_loaded)
                    return instance
            except json.JSONDecodeError:
                logger.error(f"JSON decode error: {response}")
                pass
            prompt = self.retry_prompt.render(summarizeTitleExample)
            response = self.llm_client.generate_response(prompt)
        logger.error(f"Failed to parse response after {self.max_retry_count} attempts.")
     
