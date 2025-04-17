"""
OpenRouter接口模块
用于处理与OpenRouter API的交互
"""

import json, requests, time
from typing import Any, List, Mapping, Optional, Literal, Union, TypedDict

class OpenRouter:
    """
    OpenRouter接口类
    管理与OpenRouter API的通信
    """

    Message_Type = TypedDict('Message', { 'role': Literal['user', 'assistant', 'system', 'tool'], 'content': str })
    ProviderPreferences_Type = TypedDict(
        'ProviderPreferences', {
            'allow_fallbacks': Optional[bool],
            'require_parameters': Optional[bool],
            'data_collection': Union[Literal['deny'], Literal['allow'], None],
            'order': Optional[List[Literal[
                'OpenAI', 'Anthropic', 'HuggingFace', 'Google', 'Together', 'DeepInfra', 'Azure', 'Modal',
                'AnyScale', 'Replicate', 'Perplexity', 'Recursal', 'Fireworks', 'Mistral', 'Groq', 'Cohere',
                'Lepton', 'OctoAI', 'Novita', 'DeepSeek', 'Infermatic', 'AI21', 'Featherless', 'Mancer',
                'Mancer 2', 'Lynn 2', 'Lynn'
            ]]]
        }, total=False
    )

    def __init__(self,
        api_key: str,
        provider: Optional[ProviderPreferences_Type] | None = None,
        model: str = "microsoft/wizardlm-2-7b",
        max_tokens: int = 0,
        temperature: Optional[float] | None = 1.0,
        top_k: Optional[int] | None = 0.0,
        top_p: Optional[float] = 1.0,
        presence_penalty: Optional[float] = 0.0,
        frequency_penalty: Optional[float] = 0.0,
        repetition_penalty: Optional[float] = 1.0,
        min_p: Optional[float] = 0.0,
        top_a: Optional[float] = 0.0,
        seed: Optional[int] | None = None,
        logit_bias: Optional[Mapping[int, int]] | None = None,
        response_format: Optional[Mapping[str, str]] | None = None,
        stop: Optional[Mapping[str, str]] | None = None,
        set_p50: bool = False,
        set_p90: bool = False,
        api_url: str = "https://openrouter.ai/api/v1/chat/completions",
        timeout: int = 3600,
        ):

        self.api_url = api_url
        self.api_key = api_key
        self.provider = provider
        self.model = model
        self.max_tokens = max_tokens
        self.seed = seed
        self.logit_bias = logit_bias
        self.response_format = response_format
        self.stop = stop
        self.timeout = timeout

        # Get the top LLM sampling parameter configurations used by users on OpenRouter.
        # https://openrouter.ai/docs/parameters-api
        if (set_p90 or set_p50):
            parameters_url = f'https://openrouter.ai/api/v1/parameters/{self.model}'
            headers = {
                'accept': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            params = requests.get(parameters_url, headers=headers).json()["data"]
            # I am so sorry
            self.temperature = params["temperature_p50"] if set_p50 else params["temperature_p90"]
            self.top_k = params["top_k_p50"] if set_p50 else params["top_k_p90"]
            self.top_p = params["top_p_p50"] if set_p50 else params["top_p_p90"]
            self.presence_penalty = params["presence_penalty_p50"] if set_p50 else params["presence_penalty_p90"]
            self.frequency_penalty = params["frequency_penalty_p50"] if set_p50 else params["frequency_penalty_p90"]
            self.repetition_penalty = params["repetition_penalty_p50"] if set_p50 else params["repetition_penalty_p90"]
            self.min_p = params["min_p_p50"] if set_p50 else params["min_p_p90"]
            self.top_a = params["top_a_p50"] if set_p50 else params["top_a_p90"]
        else: 
            self.temperature = temperature 
            self.top_k = top_k 
            self.top_p = top_p 
            self.presence_penalty = presence_penalty 
            self.frequency_penalty = frequency_penalty 
            self.repetition_penalty = repetition_penalty 
            self.min_p = min_p 
            self.top_a = top_a 

    def set_params(self, **kwargs):
        """
        设置生成参数
        
        参数:
            **kwargs: 参数键值对
        """
        self.params = kwargs

    def ensure_array(self,
            input_msg: List[Message_Type] | Message_Type
        ) -> List[Message_Type]:
        if isinstance(input_msg, (list, tuple)):
            return input_msg
        else:
            return [input_msg]

    def chat(self, messages, seed=None):
        """
        发送聊天请求
        
        参数:
            messages (list): 消息列表
            seed (int): 随机种子
            
        返回:
            str: API响应文本
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages
        }
        
        if seed is not None:
            data["seed"] = seed
            
        if self.params:
            data.update(self.params)
            
        response = requests.post(
            f"{self.api_url}/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            raise Exception(f"API请求失败: {response.text}")
            
        try:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"解析API响应失败: {str(e)}")
