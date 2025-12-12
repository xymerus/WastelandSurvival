# 文件路径: WastelandSurvival/src/models/player.py
import config

class Player:
    def __init__(self, name):
        self.name = name
        self.max_hp = 100
        self.hp = 100
        self.hunger = 100
        self.inventory = [] 
        self.companions = []
        self.is_alive = True
        self.base_damage = 5
        
        # === RPG 新增属性 ===
        self.xp = 0
        self.level = 1
        self.xp_to_next_level = 100

    def gain_xp(self, amount):
        self.xp += amount
        # 升级逻辑
        if self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level += 1
            self.max_hp += 10       # 升级加血上限
            self.hp = self.max_hp   # 升级回满血
            self.base_damage += 2   # 升级加攻击
            self.xp_to_next_level = int(self.xp_to_next_level * 1.5) # 下一级更难
            return True # 返回 True 表示升级了
        return False

    def get_attack_damage(self):
        dmg = self.base_damage + (self.level * 2) # 等级加成
        
        # 武器加成
        if "霰弹枪" in self.inventory: dmg += 45
        elif "警用手枪" in self.inventory: dmg += 20
        elif "生锈铁管" in self.inventory: dmg += 5
        
        # 伙伴加成
        if "流浪狗旺财" in self.companions: dmg += 10
        if "老兵" in self.companions: dmg += 15
        return dmg

    # (以下基础方法保持不变，请保留)
    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0: self.hp=0; self.is_alive=False
    def move(self): self.hunger -= config.HUNGER_COST_MOVE; self._check_status()
    def search(self): self.hunger -= config.HUNGER_COST_SEARCH; self._check_status()
    def get_item(self, item): self.inventory.append(item)
    def remove_item(self, item): 
        if item in self.inventory: self.inventory.remove(item); return True
        return False
    def restore(self, hp=0, hunger=0):
        self.hp+=hp; self.hunger+=hunger
        if self.hp>self.max_hp: self.hp=self.max_hp
        if self.hunger>100: self.hunger=100
    def _check_status(self):
        if self.hunger<=0: self.hunger=0; self.take_damage(5)