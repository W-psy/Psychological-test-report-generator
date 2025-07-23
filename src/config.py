"""
心理测试反馈报告生成器 - 配置管理模块
负责管理应用程序的各种配置参数
"""

import json
import os
from pathlib import Path
from typing import Dict, Any

class Config:
    """配置管理类"""
    
    def __init__(self):
        self.config_file = Path("config.json")
        self.default_config = self._get_default_config()
        self.config = self._load_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "app": {
                "title": "心理测试反馈报告生成器",
                "version": "1.0.2",
                "window_size": "1000x700",
                "theme": "light"
            },
            "paths": {
                "last_data_file": "",
                "last_image_dir": "",
                "last_output_dir": "",
                "default_output_dir": "./reports"
            },
            "report": {
                "page_size": "A4",
                "margins": {
                    "left": 1.5,
                    "right": 1.5,
                    "top": 1.0,
                    "bottom": 0.5
                },
                "fonts": {
                    "title": "SimHei",
                    "header": "SimHei", 
                    "body": "SimSun",
                    "note": "SimKai"
                }
            },
            "tasks": {
                "regular_tasks": [],
                "special_tasks": []
            },
            "evaluation": {
                "thresholds": {
                    "low": 85,
                    "high": 115
                }
            }
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 合并默认配置，确保所有必要的键都存在
                return self._merge_config(self.default_config, config)
            except Exception as e:
                print(f"配置文件加载失败，使用默认配置: {e}")
                return self.default_config.copy()
        else:
            return self.default_config.copy()
    
    def _merge_config(self, default: Dict, loaded: Dict) -> Dict:
        """递归合并配置，确保所有默认键都存在"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"配置文件保存失败: {e}")
    
    def get(self, key_path: str, default=None):
        """获取配置值，支持点号分隔的路径"""
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, key_path: str, value):
        """设置配置值，支持点号分隔的路径"""
        keys = key_path.split('.')
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
    
    def update_last_paths(self, data_file=None, image_dir=None, output_dir=None):
        """更新最近使用的路径"""
        if data_file:
            self.set("paths.last_data_file", str(data_file))
        if image_dir:
            self.set("paths.last_image_dir", str(image_dir))
        if output_dir:
            self.set("paths.last_output_dir", str(output_dir))
        self.save_config()

# 全局配置实例
app_config = Config()