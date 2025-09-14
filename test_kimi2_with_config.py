"""
Test script for Kimi2 model configuration using youtu-agent config
"""
import os
from openai import OpenAI
from utu.config import ConfigLoader

# Load the Kimi2 model configuration
config = ConfigLoader.load_model_config('kimi2')
print("Model config:")
print(f"  Type: {config.model_provider.type}")
print(f"  Model: {config.model_provider.model}")
print(f"  Base URL: {config.model_provider.base_url}")

# Get the API key from environment variable
api_key = os.getenv("MOONSHOT_API_KEY")
if not api_key:
    print("MOONSHOT_API_KEY environment variable not set")
    print("Please set your Moonshot API key as an environment variable:")
    print("  set MOONSHOT_API_KEY=your_actual_api_key_here")
    exit(1)

print(f"API Key set: {bool(api_key)}")

client = OpenAI(
    api_key=api_key,
    base_url=config.model_provider.base_url,
)

try:
    print("Sending request to Kimi2 model...")
    completion = client.chat.completions.create(
        model=config.model_provider.model,
        messages=[
            {"role": "system", "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。"},
            {"role": "user", "content": "你好，我叫李雷，1+1等于多少？"}
        ],
        temperature=0.6,
    )
    
    print("Kimi2 model test successful!")
    print("Response:", completion.choices[0].message.content)
    
except Exception as e:
    print(f"Error testing Kimi2 model: {e}")
    import traceback
    traceback.print_exc()