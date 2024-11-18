import os
import yaml
from typing import Dict, Optional

class ConfigManager:
    DEFAULT_CONFIG = {
        "language": "en",  # Default to English (en/zh-CN/zh-TW)
        "language_model": "ollama",
        "model": "qwen2.5-coder:7b",
        "endpoint": "http://localhost:11434",
        "api_key": "ollama"
    }
    
    def __init__(self):
        self.config_path = os.path.expanduser("~/.git-sage/config.yml")
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Load configuration file, create default config if it doesn't exist"""
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
        return self.config.get("endpoint", "http://localhost:11434")
    
    def get_api_key(self) -> str:
        """Get API key"""
        return self.config.get("api_key", "ollama")
    
    def update_config(self, key: str, value: str) -> None:
        """Update configuration item"""
        self.config[key] = value
        self.save_config(self.config)
