"""
LLM API 客户端
支持多模型自动重试和故障转移
"""

import json
import time
import requests
from typing import Optional
import os


class LLMClient:
    """LLM API 客户端 - 支持多模型重试"""

    DEFAULT_API_URL = "https://x666.me/v1/chat/completions"

    # 模型优先级列表（按顺序尝试）
    MODEL_PRIORITY = [
        "claude-opus-4-5-thinking",
        "gpt-5.2",
        "gemini-3-pro-high",
        "gemini-3-flash-preview",
        "gemini-2.5-pro-1m",
    ]

    # 重试配置
    MAX_RETRIES = 30
    RETRY_DELAY = 30  # 秒

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        models: Optional[list[str]] = None,
        max_retries: int = MAX_RETRIES,
        retry_delay: int = RETRY_DELAY
    ):
        """
        初始化 LLM 客户端

        Args:
            api_key: API Key
            api_url: API URL
            models: 模型优先级列表
            max_retries: 最大重试次数
            retry_delay: 重试间隔（秒）
        """
        self.api_key = api_key or os.environ.get("LLM_API_KEY")
        self.api_url = api_url or os.environ.get("LLM_API_URL", self.DEFAULT_API_URL)
        self.models = models or self.MODEL_PRIORITY
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        if not self.api_key:
            raise ValueError("LLM_API_KEY 未设置")

    def chat(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        verbose: bool = True
    ) -> str:
        """
        发送聊天请求（带多模型重试）

        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            temperature: 温度参数
            max_tokens: 最大 token 数
            verbose: 是否打印详细日志

        Returns:
            模型响应文本
        """
        # 打印完整 Prompt（用于调试）
        if verbose:
            print("\n" + "=" * 70)
            print("🧠 AI 思考过程 - 发送给 LLM 的完整 Prompt")
            print("=" * 70)
            if system_prompt:
                print(f"[System Prompt]\n{system_prompt}\n")
            print(f"[User Prompt]\n{prompt}")
            print("=" * 70 + "\n")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        total_attempts = 0
        model_index = 0

        while total_attempts < self.max_retries:
            current_model = self.models[model_index % len(self.models)]
            total_attempts += 1

            print(f"  🤖 尝试 {total_attempts}/{self.max_retries}: {current_model}")

            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json={
                        "model": current_model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    },
                    timeout=120
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    if content:
                        print(f"  ✅ {current_model} 成功")
                        # 打印完整 LLM 响应
                        if verbose:
                            print("\n" + "=" * 70)
                            print("🎯 AI 思考过程 - LLM 完整响应")
                            print("=" * 70)
                            print(content)
                            print("=" * 70 + "\n")
                        return content

                # 记录错误
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get("message", error_msg)
                except:
                    pass

                print(f"  ⚠️ {current_model} 失败: {error_msg}")

            except requests.exceptions.Timeout:
                print(f"  ⚠️ {current_model} 超时")
            except requests.exceptions.RequestException as e:
                print(f"  ⚠️ {current_model} 网络错误: {e}")
            except Exception as e:
                print(f"  ⚠️ {current_model} 异常: {e}")

            # 切换到下一个模型
            model_index += 1

            # 如果还有重试机会，等待后继续
            if total_attempts < self.max_retries:
                print(f"  ⏳ 等待 {self.retry_delay} 秒后重试...")
                time.sleep(self.retry_delay)

        raise Exception(f"所有模型均失败，共尝试 {total_attempts} 次")

    def chat_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> dict:
        """
        发送聊天请求并解析 JSON 响应

        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            temperature: 温度参数

        Returns:
            解析后的 JSON 字典
        """
        response = self.chat(prompt, system_prompt, temperature)

        # 尝试提取 JSON
        try:
            # 尝试直接解析
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # 尝试从 markdown 代码块中提取
        import re
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # 尝试找到 JSON 对象
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        raise ValueError(f"无法解析 JSON 响应: {response[:500]}")


if __name__ == "__main__":
    # 测试
    client = LLMClient()
    response = client.chat("你好，请简短回复")
    print(f"响应: {response}")
