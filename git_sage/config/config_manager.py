import os
import yaml
from typing import Dict, Optional

class ConfigManager:
    DEFAULT_CONFIG = {
        "language": "en",  # 默认使用英文
        "language_model": "ollama",  # 选择使用的语言模型服务（如ollama或其他在线服务）
        "model": "codellama",  # 选择具体的模型名称
        "model_endpoint": "http://localhost:11434",  # 模型服务地址
        "api_key": "ollama",  # 默认key
    }
    
    def __init__(self):
        self.config_path = os.path.expanduser("~/.git-sage/config.yml")
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """加载配置文件，如果不存在则创建默认配置"""
        if not os.path.exists(self.config_path):
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return {**self.DEFAULT_CONFIG, **(config or {})}
        except Exception as e:
            print(f"Warning: Failed to load config file: {e}")
            return self.DEFAULT_CONFIG
    
    def save_config(self, config: Dict) -> None:
        """保存配置到文件"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True)
    
    def get_language(self) -> str:
        """获取当前配置的语言"""
        return self.config.get("language", "en")
    
    def get_language_model(self) -> str:
        """获取当前使用的语言模型服务类型（如ollama或其他在线服务）"""
        return self.config.get("language_model", "ollama")
    
    def get_model(self) -> str:
        """获取当前选择的具体模型名称"""
        return self.config.get("model", "codellama")
    
    def get_model_endpoint(self) -> str:
        """获取模型服务地址"""
        return self.config.get("model_endpoint", "http://localhost:11434")
    
    def get_api_key(self) -> str:
        """获取API密钥"""
        return self.config.get("api_key", "ollama")
    
    def update_config(self, key: str, value: str) -> None:
        """更新配置项"""
        self.config[key] = value
        self.save_config(self.config)
