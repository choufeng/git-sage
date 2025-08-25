import os
import yaml
from typing import Dict, Optional

class ConfigManager:
    DEFAULT_CONFIG = {
        "language": "en",  # Default to English (en/zh-CN/zh-TW)
        "language_model": "ollama",  # 可选: ollama/openrouter/deepseek/gemini/modelscope
        "model": "qwen2.5-coder:7b",
        "api_key": "ollama"
    }
    
    DEFAULT_MODELS = {
        "ollama": "qwen2.5-coder:7b",
        "openrouter": "anthropic/claude-3-sonnet",
        "deepseek": "deepseek-chat",
        "gemini": "gemini-2.5-flash",
        "modelscope": "Qwen/Qwen3-Coder-480B-A35B-Instruct"
    }
    
    # 默认端点地址
    OLLAMA_ENDPOINT = "http://localhost:11434"
    OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1"
    DEEPSEEK_ENDPOINT = "https://api.deepseek.com/v1"
    GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta"
    MODELSCOPE_ENDPOINT = "https://api-inference.modelscope.cn/v1/chat/completions"
    
    def __init__(self):
        self.config_path = os.path.expanduser("~/.git-sage/config.yml")
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load configuration file, create default config if it doesn't exist"""
        if not os.path.exists(self.config_path):
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            initial_config = self.DEFAULT_CONFIG.copy()
            initial_config["endpoint"] = self.OLLAMA_ENDPOINT  # 设置初始endpoint
            self.save_config(initial_config)
            return initial_config
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return {**self.DEFAULT_CONFIG, **(config or {})}
        except Exception as e:
            print(f"Warning: Failed to load config file: {e}")
            return self.DEFAULT_CONFIG
    
    def save_config(self, config: Dict) -> None:
        """Save configuration to file"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True)
    
    def get_language(self) -> str:
        """Get currently configured language"""
        return self.config.get("language", "en")
    
    def get_language_model(self) -> str:
        """Get current language model service type"""
        return self.config.get("language_model", "ollama")
    
    def get_model(self) -> str:
        """Get current specific model name"""
        return self.config.get("model", "qwen2.5-coder:7b")
    
    def get_model_endpoint(self) -> str:
        """Get model service endpoint"""
        return self.config.get("endpoint", self.OLLAMA_ENDPOINT)
    
    def get_api_key(self) -> str:
        """Get API key"""
        return self.config.get("api_key", "ollama")
    
    def update_config(self, key: str, value: str) -> None:
        """Update configuration item"""
        # 如果是更新language_model
        if key == "language_model":
            # 只有当language_model真的改变时才更新endpoint和model
            if value != self.config.get("language_model"):
                if value == "ollama":
                    self.config["endpoint"] = self.OLLAMA_ENDPOINT
                    self.config["model"] = self.DEFAULT_MODELS["ollama"]
                elif value == "openrouter":
                    self.config["endpoint"] = self.OPENROUTER_ENDPOINT
                    self.config["model"] = self.DEFAULT_MODELS["openrouter"]
                elif value == "deepseek":
                    self.config["endpoint"] = self.DEEPSEEK_ENDPOINT
                    self.config["model"] = self.DEFAULT_MODELS["deepseek"]
                elif value == "gemini":
                    self.config["endpoint"] = self.GEMINI_ENDPOINT
                    self.config["model"] = self.DEFAULT_MODELS["gemini"]
                elif value == "modelscope":
                    self.config["endpoint"] = self.MODELSCOPE_ENDPOINT
                    self.config["model"] = self.DEFAULT_MODELS["modelscope"]
                else:
                    self.config["endpoint"] = ""
                    self.config["model"] = ""
            # 无论是否更新endpoint，都要更新language_model
            self.config["language_model"] = value
        
        # 如果是直接设置endpoint
        elif key == "endpoint":
            self.config["endpoint"] = value
        
        # 其他配置项的更新
        else:
            self.config[key] = value
        
        self.save_config(self.config)
