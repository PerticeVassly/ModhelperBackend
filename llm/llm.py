from typing import Dict, List, Union
from openai import OpenAI
import json
from config import settings

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
                 stream: bool = False):
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self.temperature = termperature
        self.max_tokens = max_tokens
        self.messages = []
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
        # add the interaction to the message history
        self.messages.append({"role": "user", "content": prompt})
        self.messages.append({"role": "assistant", "content": reponse.choices[0].message.content})
        # todo() how to handle the stream response ?
        if self.stream:
            return reponse
        else:
            return reponse.choices[0].message.content
    

class ExtractorLLM():
    """
    LLM to extract the key words from the user input."""
    def __init__(self, 
                 llm_client: LLMClient):
        self.max_retry_count = 3
        self.llm_client = llm_client
        self.extract_template = """
            你是一名专业的 Minecraft Mod 解析助手，擅长从文本中提取关键信息。
            请从所给的文本中提取：
            - **MCMod 名称**（即 Mod 的名称，如果有多个，请全部列出）
            - **版本号**（如果有多个，请全部列出）
            - **物品名称**（以列表形式返回）
            - **世界名称**（如果有多个，请全部列出）

            请严格使用 JSON 格式返回结果，不要有额外输出，格式如下例：
            {{
            "mods": ["Mod1", "Mod2"],
            "versions": ["1.16.5", "1.12.2"],
            "items": ["钻石剑", "附魔书"],
            "worlds": ["虚空世界", "暮色森林"]
            }}

            **文本：**
            {input_text}
            """
        self.retry_template = """
            你的回答格式不正确，请严格按照以下格式例子返回结果：
            {{
            "mods": ["Mod1", "Mod2"],
            "versions": ["1.16.5", "1.12.2"],
            "items": ["钻石剑", "附魔书"],
            "worlds": ["虚空世界", "暮色森林"]
            }}
            """

    def extract(self, input_text: str):
        print("Extracting keywords from input text...")
        print("Input text: ", input_text)
        prompt = self.extract_template.format(input_text=input_text)
        response = self.llm_client.generate_response(prompt)
        if (settings.DEBUG):
            print("Response: ", response)
            print("Response type: ", type(response))
        checked_response = self.check_response_format(response)
        return checked_response
    
    def check_response_format(self, response: str):
        response = response.replace("```json", "").replace("```", "").strip()
        if (settings.DEBUG):
            print("Now response: ", response)
        for i in range(self.max_retry_count):
            try:
                response = json.loads(response)
                if isinstance(response, dict) and all(key in response for key in ["mods", "versions", "items", "worlds"]):
                    return response
            except json.JSONDecodeError:
                if (settings.DEBUG):
                    print("Response format is incorrect, retrying...")
            response = self.llm_client.generate_response(self.extract_template)
        raise ValueError("LLM can't generate the formated response. Please check whether the LLM you choose is not stable or your prompt is not clear enough")

class RAGLLM():
    """
    A class interacting with a LLM with retrieval context.
    """

    def __init__(self, 
                 llm_client: LLMClient,
                 context: List[Dict[str, str]]):
        self.llm_client = llm_client
        self.prompt_template = """
            你是一名专业的 Minecraft Mod 解析助手.
            我们将给你一些 Minecraft Mod 的相关信息，请你根据这些信息回答问题。
            {context}
            问题：{question}"
            """

    def __format_context(self, context: List[Dict[str, str]]) -> str:
        formatted_context = ""
        for item in context:
            formatted_context += "这是关于“{}” 的参考资料：\n".format(item.get("description"))
            formatted_context += item.get("content") + "\n"
        return formatted_context

    def generate_response(
        self, 
        question: str, 
        context: List[Dict[str, str]] = None
    ) -> str:
        formatted_context = self.__format_context(context or self.context)
        prompt = self.prompt_template.format(context=formatted_context, question=question)
        response = self.llm_client.generate_response(prompt)
        return response
        
    

      
 
