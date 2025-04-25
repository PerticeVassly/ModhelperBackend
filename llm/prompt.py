from abc import ABC, abstractmethod
from typing import List
import logging
import textwrap
from model import MessageInfo

logger = logging.getLogger("prompt")

class Prompt(ABC):
    """
    Basic class for all prompts.

    Contaings a template and method of how to render it.
    """
    def __init__(self, template: str):
        self.template = template

    @abstractmethod
    def render(self, kwargs : list[str]) -> str:
        pass

class ExtractorPrompt(Prompt):

    def __init__(self):
        template = textwrap.dedent("""
            你是一名专业的{topic_name}解析助手，擅长从文本中提取关键信息。
            请从所给的文本中提取涉及{extraction_fields}的信息，如果有多个，请全部列出。
            请严格使用JSON格式返回结果，不要有额外输出，格式如下例：
            {{
                {json_format}
            }}
            文本: {input_text}
        """)
        super().__init__(template)

    def render(self, key_words: List[str], topic_name : str, input_text : str) -> str:
        extraction_fields = "\n".join(f"**{kw}**" for kw in key_words)
        json_format = ",\n".join(f'"{kw}": []' for kw in key_words)
        ans = self.template.format(
            topic_name=topic_name,
            extraction_fields=extraction_fields,
            json_format=json_format,
            input_text=input_text
        )
        return ans

class RetryPrompt(Prompt):
    def __init__(self):
        template = textwrap.dedent("""
            你的回答格式不正确，请严格按照以下格式返回结果：
            {{
                {json_format}
            }}
        """)
        super().__init__(template)

    def render(self, key_words: List[str]) -> str:
        json_format = ",\n".join(f'"{kw}": []' for kw in key_words)
        ans = self.template.format(json_format=json_format)
        return ans
      
class RAGPrompt(Prompt):
    def __init__(self):
        template = textwrap.dedent("""
            你是一名专业的{topic_name}助手.
            我们将给你一些{topic_name}相关参考资料，请你根据这些信息回答问题，但是你不能直接引用这些信息，也不能在回答中透露出你是从这些信息中获取的答案。
            参考资料：{context}
            问题：{question}
        """)
        super().__init__(template)

    def render(self, context_content: str, question: str, topic_name : str) -> str:
        ans = self.template.format(
            topic_name=topic_name,
            context=context_content,
            question=question
        )
        return ans

class NonRAGPrompt(Prompt):
    def __init__(self):
        template = textwrap.dedent("""
            {question}
        """)
        super().__init__(template)

    def render(self, question) -> str:
        ans = self.template.format(
            question=question
        )
        return ans
    
class SummarizePrompt(Prompt):
    def __init__(self):
        template = textwrap.dedent("""
            你是一名对话助手，擅长为对话内容生成简短的概括性标题。
            请根据以下对话内容，评估原始标题是否仍能概括此段对话。若能，请返回原始标题；若不能，请生成一个新的标题。
            请严格使用JSON格式返回结果，不要有额外输出，格式如下例：
            {{
                "title": ["概括或者复用的标题"]
            }}
            原始标题：{old_name}
            对话内容：{conversation_messages}
        """)
        super().__init__(template)

    def render(self, messages: List[MessageInfo], old_name : str) -> str:
        ans = self.template.format(
            old_name=old_name,
            conversation_messages="\n".join(f"user: {m.user_message}\nassistant: {m.assistant_message}" for m in messages)
        )
        return ans
