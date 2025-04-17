from typing import Dict, List, Union
from openai import OpenAI
import copy

import logging

logger = logging.getLogger("llm")

class LLMClient():
    """
    A Basic client for interacting with a large language model (LLM) API.
    """
    def __init__(self, 
                 model_name: str = "deepseek-chat",
                 api_key: str = None, 
                 base_url: str = "https://api.deepseek.com",
                 termperature: float = 0.7,
                 max_tokens: int = 1000,
                 stream: bool = False,
                 messages: List[Dict[str, str]] = []):
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
    ) -> Union[str, List[Dict[str, any]]]:
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
    



        
    

      
 
