import json
import os
from typing import Dict, List

class ConfigManager:
    def __init__(self, config_file='buttons.json'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return self.create_default_config()
        return self.create_default_config()
    
    def save_config(self) -> None:
        """保存配置到文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)
    
    def create_default_config(self) -> Dict:
        """创建默认配置"""
        return {
            "buttons": [],
            "settings": {
                "opacity": 0.8,
                "auto_hide": True,
                "position": {"x": 0, "y": 0}
            }
        }
    
    def add_button(self, button_config: Dict) -> None:
        """添加按钮配置"""
        self.config["buttons"].append(button_config)
        self.save_config()
    
    def remove_button(self, index: int) -> None:
        """删除按钮配置"""
        if 0 <= index < len(self.config["buttons"]):
            self.config["buttons"].pop(index)
            self.save_config()
    
    def update_button_order(self, new_order: List[int]) -> None:
        """更新按钮顺序"""
        buttons = self.config["buttons"]
        self.config["buttons"] = [buttons[i] for i in new_order]
        self.save_config()
    
    def update_position(self, x: int, y: int) -> None:
        """更新工具栏位置"""
        self.config["settings"]["position"] = {"x": x, "y": y}
        self.save_config()
    
    def update_opacity(self, opacity: float) -> None:
        """更新透明度"""
        self.config["settings"]["opacity"] = opacity
        self.save_config()
    
    def update_auto_hide(self, auto_hide: bool) -> None:
        """更新自动隐藏设置"""
        self.config["settings"]["auto_hide"] = auto_hide
        self.save_config()
    
    def get_buttons(self) -> List[Dict]:
        """获取所有按钮配置"""
        return self.config["buttons"]
    
    def get_settings(self) -> Dict:
        """获取全局设置"""
        return self.config["settings"]