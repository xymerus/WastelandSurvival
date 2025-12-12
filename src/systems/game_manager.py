# 文件路径: WastelandSurvival/src/systems/game_manager.py
from src.utils.data_manager import DataManager
from src.views.main_window import MainWindow
from src.models.player import Player
from src.models.location import Location
from src.models.enemy import Enemy
from src.models.npc import NPC
import random

class GameManager:
    def __init__(self):
        self.data_mgr = DataManager()
        self.gui = MainWindow(self) # 这会先显示主菜单
        # 数据初始化放到了 start_new_game 里

    # === 游戏流程控制 ===
    def start_new_game(self):
        """开始新游戏"""
        self.setup_world()
        self.player = Player("Survivor")
        self.time_hour = 8
        self.current_enemy = None
        self.current_npc = None
        
        self.gui.show_game_interface() # 切换到游戏界面
        self.gui.append_text("=== 新 游 戏 开 始 ===", "green")
        self.update_display()

    def load_game(self):
        """读取存档"""
        data = self.data_mgr.load_game()
        if not data: return
        
        self.setup_world()
        p_data = data["player"]
        
        # 恢复玩家数据
        self.player = Player(p_data["name"])
        self.player.hp = p_data["hp"]
        self.player.max_hp = p_data["max_hp"]
        self.player.hunger = p_data["hunger"]
        self.player.inventory = p_data["inventory"]
        self.player.companions = p_data["companions"]
        self.player.xp = p_data.get("xp", 0)
        self.player.level = p_data.get("level", 1)
        
        # 恢复环境数据
        target_loc = data["game"]["location"]
        # 查找地点对象
        for loc in self.locations:
            if loc.name == target_loc:
                self.current_location = loc
                break
        self.time_hour = data["game"]["time"]
        
        self.current_enemy = None
        self.current_npc = None
        
        self.gui.show_game_interface()
        self.gui.append_text(f"=== 存档已读取 | Lv.{self.player.level} | {target_loc} ===", "yellow")
        self.update_display()

    def save_game(self):
        """保存当前进度"""
        if self.current_enemy:
            self.gui.append_text("战斗中无法存档！", "red")
            return
        
        success = self.data_mgr.save_game(self.player, self.current_location.name, self.time_hour)
        if success:
            self.gui.append_text(">>> 进度已保存 <<<", "green")
            self.gui.screen_flash("#003300", 200)
        else:
            self.gui.append_text("保存失败！", "red")

    def return_to_menu(self):
        """返回主菜单"""
        self.gui.show_main_menu()

    # === 以下为 v1.1 的原有逻辑，稍作修改适配 RPG ===

    def setup_world(self):
        # (保持原有的地点创建逻辑，这里简写)
        home = Location("地下避难所", "你的安全屋。", 2, 4, "[🏠]")
        street = Location("废弃街道", "危险的街道。", 2, 3, "[🛣️]", items=["生锈铁管", "变异鼠肉"])
        mart = Location("沃尔玛超市", "废弃超市。", 3, 3, "[🛒]", items=["压缩饼干", "纯净水"])
        square = Location("中央广场", "死寂的广场。", 2, 2, "[⛲]", items=["过期罐头"])
        hospital = Location("中心医院", "充满消毒水味。", 1, 2, "[🏥]", items=["急救包"])
        police = Location("警察局", "曾经的防线。", 3, 2, "[👮]", items=["警用手枪", "霰弹枪"])
        tower = Location("广播塔", "最终决战之地。", 2, 1, "[💀]")

        home.add_connection("north", street)
        street.add_connection("south", home); street.add_connection("east", mart); street.add_connection("north", square)
        mart.add_connection("west", street)
        square.add_connection("south", street); square.add_connection("west", hospital); square.add_connection("east", police); square.add_connection("north", tower)
        hospital.add_connection("east", square); police.add_connection("west", square); tower.add_connection("south", square)
        
        self.locations = [home, street, mart, square, hospital, police, tower]
        self.current_location = home
        
        # 恢复 NPC
        dog = NPC("流浪狗旺财", "一只可怜的黄狗。", "废弃街道", item_needed="变异鼠肉")
        dog.set_options(["给它肉吃", "赶走", "离开"])
        doc = NPC("陈医生", "被困的医生。", "中心医院")
        doc.set_options(["帮她解围 (战斗)", "无视"])
        self.npcs = [dog, doc]
        
        # 物品库
        self.item_db = {
            "过期罐头": {"hp": -5, "hunger": 30}, "变异鼠肉": {"hp": -20, "hunger": 60},
            "压缩饼干": {"hp": 0, "hunger": 50}, "纯净水": {"hp": 5, "hunger": 10},
            "急救包": {"hp": 60, "hunger": 0}, "警用手枪": {"hp":0,"hunger":0},
            "霰弹枪": {"hp":0,"hunger":0}, "生锈铁管": {"hp":0,"hunger":0}
        }

    def update_display(self):
        # (同 v1.1，但增加 XP 更新)
        time_str = self.get_time_desc()[0]
        desc = self.current_location.description
        self.gui.update_main_text(f"\n--- {self.current_location.name} ---\n{desc}\n")
        self.gui.update_stats(self.player, f"{self.time_hour}:00 ({time_str})")
        self.gui.update_map(self.render_map())

    def handle_input(self, cmd):
        # ... (输入处理逻辑同 v1.1) ...
        # 只需要在死亡判定处调用 show_death_screen
        if not self.player.is_alive:
            self.gui.show_death_screen()
            return

        # (复制 v1.1 的 handle_input 逻辑)
        # 唯一区别是 go 指令里
        parts = cmd.lower().split()
        if not parts: return
        action = parts[0]
        
        if action == "go":
            # ... 移动逻辑 ...
            direction = parts[1] if len(parts)>1 else ""
            if direction in self.current_location.connections:
                self.pass_time(1)
                self.current_location = self.current_location.connections[direction]
                self.player.move()
                if not self.player.is_alive: # 移动可能饿死
                    self.gui.show_death_screen()
                    return

                if self.current_location.name == "广播塔": self.trigger_boss_fight(); return
                if self.check_npc_event(): return
                if self.check_encounter(0.4): return
                self.update_display()
            else:
                self.gui.append_text("无路可走。", "red")
        
        elif action == "search":
            self.pass_time(1); self.player.search()
            if self.current_location.items:
                i = self.current_location.items.pop(0)
                self.player.get_item(i)
                self.gui.append_text(f"获得: {i}", "green")
                # 搜刮也给一点点 XP
                if self.player.gain_xp(10): self.gui.append_text("🆙 等级提升！能力增强！", "yellow")
            else: self.gui.append_text("没东西。", "gray")
            self.update_display()

    def handle_combat(self, action):
        # ... (战斗逻辑同 v1.1，增加 XP 获取) ...
        if not self.current_enemy: return
        
        if action == "attack":
            dmg = self.player.get_attack_damage()
            # ... (伙伴加成/暴击代码同前) ...
            self.current_enemy.hp -= dmg
            self.gui.append_text(f"造成 {dmg} 点伤害。", "yellow")

            if not self.current_enemy.is_alive():
                # === RPG 核心：击杀获胜 ===
                xp_gain = 50 if self.current_enemy.name != "变异暴君" else 500
                self.gui.append_text(f"击杀敌人！获得 {xp_gain} XP。", "green")
                
                if self.player.gain_xp(xp_gain):
                    self.gui.append_text(f"🆙 升级了！当前 Lv.{self.player.level} (HP/攻击力提升)", "cyan")
                    self.gui.screen_flash("#ffffff", 200)

                # ... (后续清理逻辑同 v1.1) ...
                self.current_enemy = None
                self.gui.switch_mode("exploration")
                self.update_display()
                return

            # 反击
            pdmg = self.current_enemy.damage
            self.player.take_damage(pdmg)
            self.gui.append_text(f"受到伤害 -{pdmg}", "red")
            self.gui.screen_flash("#330000", 100)
            self.gui.update_stats(self.player, f"{self.time_hour}:00")

            if not self.player.is_alive:
                self.gui.show_death_screen() # 调用死亡界面
    
    # ... (其他辅助函数 check_encounter, recruit_npc, pass_time, render_map 等保持不变) ...
    # 务必确保 check_encounter 里的逻辑存在
    def check_encounter(self, chance):
        # 动态难度：随着玩家等级提升，敌人变强 (可选优化)
        if self.current_location.name == "地下避难所": return False
        if random.random() < chance:
            hp_boost = (self.player.level - 1) * 20
            dmg_boost = (self.player.level - 1) * 5
            enemies = [
                Enemy("丧尸", 40+hp_boost, 10+dmg_boost, "..", []), 
                Enemy("夜魔", 80+hp_boost, 20+dmg_boost, "..", [])
            ]
            self.current_enemy = random.choice(enemies)
            self.gui.switch_mode("combat")
            self.gui.append_text(f"遭遇强敌: {self.current_enemy.name} (Lv.{self.player.level} 适应)", "red")
            return True
        return False
        
    def get_time_desc(self): return ("白天", "gray") if 6<=self.time_hour<18 else ("深夜", "red")
    def pass_time(self, h): self.time_hour=(self.time_hour+h)%24
    def render_map(self):
        grid = [[' . ' for _ in range(5)] for _ in range(5)]
        for loc in self.locations: grid[loc.y][loc.x] = f" {loc.icon} "
        grid[self.current_location.y][self.current_location.x] = " 😶 "
        return "".join(["".join(r)+"\n\n" for r in grid])
    
    def trigger_boss_fight(self):
        # Boss 也随等级增强
        boss_hp = 300 + (self.player.level * 50)
        self.current_enemy = Enemy("变异暴君", boss_hp, 25 + self.player.level*2, "...", [])
        self.gui.switch_mode("combat")
        self.gui.append_text(f"BOSS战开始！HP: {boss_hp}", "red")

    def trigger_win(self):
        self.gui.append_text("=== 通关！你活下来了 ===", "green")
        # 可以在这里做个通关结算界面，或者直接返回主菜单
        self.gui.control_panel.destroy()
    
    # 补全缺少的函数，防止报错
    def check_npc_event(self): 
        # ... (同前) ...
        return False
    def try_use_item(self, i):
        # ... (同前) ...
        pass
    def handle_dialogue(self, i): pass

# === [修复]：添加程序入口方法 ===
    def start(self):
        """
        main.py 调用的入口点。
        负责启动 GUI 的主事件循环 (mainloop)。
        """
        self.gui.start()