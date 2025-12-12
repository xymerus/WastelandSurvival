# 文件路径: WastelandSurvival/src/models/location.py
from src.data.narrative import LOCATION_DESCS
import random

class Location:
    def __init__(self, name, base_desc, x, y, icon="[ ]", items=None):
        self.name = name
        self.base_desc = base_desc # 原始简短描述
        self.x = x
        self.y = y
        self.icon = icon
        self.items = items if items else []
        self.connections = {} 

    def add_connection(self, direction, location_obj):
        self.connections[direction] = location_obj

    def get_info(self):
        # [修改] 优先从叙事库获取长描写
        # 尝试匹配地点名
        desc_list = LOCATION_DESCS.get(self.name)
        if not desc_list:
            # 模糊匹配 (比如 '废弃工厂' 匹配 'default')
            for key in LOCATION_DESCS:
                if key in self.name:
                    desc_list = LOCATION_DESCS[key]
                    break
        
        if not desc_list: desc_list = LOCATION_DESCS["default"]
        
        # 随机选取一段描写，增加新鲜感
        flavor_text = random.choice(desc_list)
        
        info = f"{flavor_text}\n"
        if self.items:
            info += f"\n(你的直觉告诉你，这片区域还散落着: {', '.join(self.items)})"
        else:
            info += "\n(这里看起来已经被搜刮一空，连只老鼠都没有。)"
        return info