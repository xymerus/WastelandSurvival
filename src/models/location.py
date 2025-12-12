# 文件路径: WastelandSurvival/src/models/location.py
class Location:
    def __init__(self, name, description, x, y, icon="[ ]", items=None):
        self.name = name
        self.description = description
        self.x = x  # 地图横坐标
        self.y = y  # 地图纵坐标
        self.icon = icon  # 在小地图上显示的符号，如 [H], [S]
        self.items = items if items else []
        self.connections = {} 

    def add_connection(self, direction, location_obj):
        self.connections[direction] = location_obj

    def get_info(self):
        info = f"\n=== {self.name} ===\n{self.description}"
        if self.items:
            info += f"\n\n你注意到地上有: {', '.join(self.items)}"
        else:
            info += "\n\n这里看起来已经被搜刮干净了。"
        return info