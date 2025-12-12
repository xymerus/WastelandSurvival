# 文件路径: WastelandSurvival/src/models/npc.py
class NPC:
    def __init__(self, name, intro, location_name, item_needed=None):
        self.name = name
        self.intro = intro               # 第一次见面时的描述
        self.location_name = location_name # 出没地点
        self.item_needed = item_needed   # 招募需要的物品 (比如狗需要肉)
        self.is_recruited = False        # 是否已入队
        self.dialogue_options = []       # 选项 ["给它食物", "离开"]

    def set_options(self, options):
        self.dialogue_options = options