# 文件路径: WastelandSurvival/src/models/enemy.py
class Enemy:
    def __init__(self, name, hp, damage, description, loot=None):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.damage = damage
        self.description = description
        self.loot = loot if loot else []

    def is_alive(self):
        return self.hp > 0