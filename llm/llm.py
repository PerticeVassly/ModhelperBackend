import json
from .prompt import *
from model import *
import logging
import copy
from openai import OpenAI, AsyncOpenAI
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
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)                           

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

    async def generate_response(
        self, 
        prompt: str, 
    ) -> Union[str, list[dict[str, any]]]:
        """
        Generate a response from the LLM using the provided prompt.
        """
        reponse = await self.client.chat.completions.create(
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
        
class ExtractLLM():
    def __init__(self, 
                 llm_client: LLMClient):
        self.max_retry_count = 3
        self.llm_client = llm_client
        self.extract_prompt = ExtractPrompt()
        self.retry_prompt = RetryPrompt()
        
    async def extract(self, input: str) -> PreProcessResult:
        prompt = self.extract_prompt.render(question=input)
        response = await self.llm_client.generate_response(prompt)
        extracted = await self.check_and_convert(response)
        return extracted
    
    async def check_and_convert(self, response: str) -> BaseModel:
        for i in range(self.max_retry_count):
            if (response.startswith("```json")):
                response = response.replace("```json", "").replace("```", "").strip()
            try:
                response_loaded = json.loads(response)
                is_valid = all(key in response_loaded for key in extracLLMResponseExample.model_dump().keys())
                if is_valid:
                    instance = PreProcessResult.model_validate(response_loaded)
                    return instance
            except json.JSONDecodeError:
                pass
            prompt = self.retry_prompt.render(extracLLMResponseExample)
            response = await self.llm_client.generate_response(prompt)
        logger.error(f"Failed to parse response after {self.max_retry_count} attempts.")

class ClassifyLLM():
    def __init__(self, 
                 llm_client: LLMClient):
        self.max_retry_count = 3
        self.llm_client = llm_client
        self.classify_prompt = ClassifyPrompt()

    async def classify(self, input: str) -> ClassifyLLMResponse:
        prompt = self.classify_prompt.render(question=input)
        response = await self.llm_client.generate_response(prompt)
        classified = await self.check_and_convert(response)
        return classified
    
    async def check_and_convert(self, response: str) -> BaseModel:
        for i in range(self.max_retry_count):
            if (response.startswith("```json")):
                response = response.replace("```json", "").replace("```", "").strip()
            try:
                response_loaded = json.loads(response)
                is_valid = all(key in response_loaded for key in classifyLLMResponseExample.model_dump().keys())
                if is_valid:
                    instance = ClassifyLLMResponse.model_validate(response_loaded)
                    return instance
            except json.JSONDecodeError:
                logger.error(f"JSON decode error: {response}")
                pass
            prompt = self.retry_prompt.render(classifyLLMResponseExample)
            response = await self.llm_client.generate_response(prompt)
        logger.error(f"Failed to parse response after {self.max_retry_count} attempts.")
    
class IntentionAnalyzeLLM():
    def __init__(self, 
                 llm_client: LLMClient):
        self.max_retry_count = 3
        self.llm_client = llm_client
        self.intention_analyze_prompt = IntentionAnalyzePrompt()

    async def analyze(self, input: str) -> IntentionAnalyzeLLMResponse:
        prompt = self.intention_analyze_prompt.render(question=input)
        response = await self.llm_client.generate_response(prompt)
        analyzed = await self.check_and_convert(response)
        return analyzed
    
    async def check_and_convert(self, response: str) -> BaseModel:
        for i in range(self.max_retry_count):
            if (response.startswith("```json")):
                response = response.replace("```json", "").replace("```", "").strip()
            try:
                response_loaded = json.loads(response)
                is_valid = all(key in response_loaded for key in intentionAnalyzeLLMResponseExample.model_dump().keys())
                if is_valid:
                    instance = IntentionAnalyzeLLMResponse.model_validate(response_loaded)
                    return instance
            except json.JSONDecodeError:
                logger.error(f"JSON decode error: {response}")
                pass
            prompt = self.retry_prompt.render(intentionAnalyzeLLMResponseExample)
            response = await self.llm_client.generate_response(prompt)
        logger.error(f"Failed to parse response after {self.max_retry_count} attempts.")
    
class HyDELLM():
    def __init__(self, 
                 llm_client: LLMClient):
        self.max_retry_count = 3
        self.llm_client = llm_client
        self.hyde_prompt = HyDEPrompt()
        self.retry_prompt = RetryPrompt()

    async def hyde(self, input: str) -> HyDELLMResponse:
        prompt = self.hyde_prompt.render(question=input)
        response = await self.llm_client.generate_response(prompt)
        return HyDELLMResponse(hyde_answer=response)
    
class SetBackLLM():
    def __init__(self, 
                 llm_client: LLMClient):
        self.max_retry_count = 3
        self.llm_client = llm_client
        self.set_back_prompt = SetBackPrompt()
        self.retry_prompt = RetryPrompt()

    async def set_back(self, input: str) -> SetBackLLMResponse:
        prompt = self.set_back_prompt.render(question=input)
        response = await self.llm_client.generate_response(prompt)
        set_back_response = await self.check_and_convert(response)
        return set_back_response
    
    async def check_and_convert(self, response: str) -> BaseModel:
        for i in range(self.max_retry_count):
            if (response.startswith("```json")):
                response = response.replace("```json", "").replace("```", "").strip()
            try:
                response_loaded = json.loads(response)
                is_valid = all(key in response_loaded for key in setBackLLMResponseExample.model_dump().keys())
                if is_valid:
                    instance = SetBackLLMResponse.model_validate(response_loaded)
                    return instance
            except json.JSONDecodeError:
                logger.error(f"JSON decode error: {response}")
                pass
            prompt = self.retry_prompt.render(setBackLLMResponseExample)
            response = await self.llm_client.generate_response(prompt)
        logger.error(f"Failed to parse response after {self.max_retry_count} attempts.")

class NonRAGLLM():
    def __init__(self, 
                 llm_client: LLMClient):
        self.llm_client = llm_client
        self.non_rag_prompt = NonRAGPrompt()

    async def chat(self, question: str) -> str:
        prompt = self.non_rag_prompt.render(question=question)
        response = await self.llm_client.generate_response(prompt)
        return response
    
class RAGLLM():
    def __init__(self, 
                 llm_client: LLMClient):
        self.llm_client = llm_client
        self.rag_prompt = RAGPrompt()

    async def chat(
        self, 
        question: str, 
        context: list[Reference] = None,
    ) -> str:
        prompt = self.rag_prompt.render(context=context, question=question)
        response = await self.llm_client.generate_response(prompt)
        return response

class SummarizeLLM():
    def __init__(self, 
                 llm_client: LLMClient):
        self.max_retry_count = 3
        self.llm_client = llm_client
        self.summarize_prompt = SummarizePrompt()
        self.retry_prompt = RetryPrompt()
        
    async def summarize(self, messages: list[MessageInfo], old_name: str) -> SummarizeLLMResponse:
        prompt = self.summarize_prompt.render(messages=messages, old_name=old_name)
        response = await self.llm_client.generate_response(prompt)
        summarized = await self.check_and_convert(response)
        return summarized
    
    async def check_and_convert(self, response: str) -> BaseModel:
        for i in range(self.max_retry_count):
            if (response.startswith("```json")):
                response = response.replace("```json", "").replace("```", "").strip()
            try:
                response_loaded = json.loads(response)
                is_valid = all(key in response_loaded for key in summarizeLLMResponseExample.model_dump().keys())
                if is_valid:
                    instance = SummarizeLLMResponse.model_validate(response_loaded)
                    return instance
            except json.JSONDecodeError:
                logger.error(f"JSON decode error: {response}")
                pass
            prompt = self.retry_prompt.render(summarizeLLMResponseExample)
            response = await self.llm_client.generate_response(prompt)
        logger.error(f"Failed to parse response after {self.max_retry_count} attempts.")

class CategorizeLLM():
    def __init__(self, 
                 llm_client: LLMClient):
        self.llm_client = llm_client
        self.max_retry_count = 3
        self.category_prompt = CategorizePrompt()

    async def categorize(self, text: str) -> CategorizeLLMResponse:
        prompt = self.category_prompt.render(user_request=text)
        response = await self.llm_client.generate_response(prompt)
        categories = await self.check_and_convert(response)
        return categories
    
    async def check_and_convert(self, response: str) -> BaseModel:
        for i in range(self.max_retry_count):
            if (response.startswith("```json")):
                response = response.replace("```json", "").replace("```", "").strip()
            try:
                response_loaded = json.loads(response)
                is_valid = all(key in response_loaded for key in categorizeLLMResponseExample.model_dump().keys())
                if is_valid:
                    instance = CategorizeLLMResponse.model_validate(response_loaded)
                    return instance
            except json.JSONDecodeError:
                logger.error(f"JSON decode error: {response}")
                pass
            prompt = self.retry_prompt.render(categorizeLLMResponseExample)
            response = await self.llm_client.generate_response(prompt)
        logger.error(f"Failed to parse response after {self.max_retry_count} attempts.")

class ModRecommendLLM():
    def __init__(self, 
                 llm_client: LLMClient):
        self.llm_client = llm_client
        self.max_retry_count = 3
        self.mod_recommendation_prompt = ModRecommendPrompt()
        self.retry_prompt = RetryPrompt()

    async def recommend(self, text: str, mods : List[ModBriefIntroduction]) -> ModRecommendLLMResponse:
        prompt = self.mod_recommendation_prompt.render(user_request=text, mods=mods)
        response = await self.llm_client.generate_response(prompt)
        return response
    
     
