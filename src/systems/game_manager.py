# 文件路径: WastelandSurvival/src/systems/game_manager.py
from src.utils.data_manager import DataManager
from src.views.main_window import MainWindow
from src.models.player import Player
from src.models.location import Location
from src.models.enemy import Enemy
from src.models.npc import NPC
from src.models.quest import Quest # [新增]
import random

class GameManager:
    def __init__(self):
        self.data_mgr = DataManager()
        self.gui = MainWindow(self)
    
    def start(self): self.gui.start()

    # (保留 start_new_game, return_to_menu, save_game, load_game, setup_world 等)
    def start_new_game(self):
        self.setup_world()
        self.player = Player("Survivor")
        self.time_hour = 8
        self.current_enemy = None; self.current_npc = None
        self.gui.show_game_interface()
        self.gui.append_text("=== v2.2 英雄之路 ===", "green")
        self.update_display()
    
    def load_game(self):
        # 简化版load，注意：这里暂时不恢复任务状态，为了演示简单。
        # 如果要完美支持，需要在 DataManager 里保存 quests 并在 load 时重建 Quest 对象。
        data = self.data_mgr.load_game()
        if not data: return
        self.setup_world()
        p_data = data["player"]
        self.player = Player(p_data["name"])
        self.player.hp = p_data["hp"]; self.player.max_hp = p_data["max_hp"]
        self.player.hunger = p_data["hunger"]; self.player.inventory = p_data["inventory"]
        self.player.companions = p_data["companions"]; self.player.xp = p_data.get("xp", 0)
        self.player.level = p_data.get("level", 1); self.player.caps = p_data.get("caps", 0)
        
        t_loc = data["game"]["location"]
        for loc in self.locations:
            if loc.name == t_loc: self.current_location = loc; break
        self.time_hour = data["game"]["time"]
        self.current_enemy = None; self.current_npc = None
        self.gui.show_game_interface()
        self.gui.append_text("=== 读档成功 ===", "gold")
        self.update_display()

    # ... (保留 save_game, return_to_menu) ...
    def save_game(self):
        if self.current_enemy: self.gui.append_text("战斗中不可存档!", "red"); return
        if self.data_mgr.save_game(self.player, self.current_location.name, self.time_hour): self.gui.append_text("进度已保存", "green")
    def return_to_menu(self): self.gui.show_main_menu()

    def setup_world(self):
        # ... (保留 v2.1 的地点设置) ...
        home = Location("地下避难所", "你的安全屋。", 2, 4, "[🏠]")
        street = Location("废弃街道", "危险的街道。", 2, 3, "[🛣️]", items=["生锈铁管", "变异鼠肉"])
        mart = Location("沃尔玛超市", "废弃超市。", 3, 3, "[🛒]", items=["压缩饼干", "纯净水"])
        square = Location("黑市广场", "流浪商人和雇佣兵的聚集地。", 2, 2, "[💰]", items=["过期罐头"])
        hospital = Location("中心医院", "充满消毒水味。", 1, 2, "[🏥]", items=["急救包"])
        police = Location("警察局", "曾经的防线。", 3, 2, "[👮]", items=["警用手枪", "霰弹枪"])
        tower = Location("广播塔", "最终决战之地。", 2, 1, "[💀]")
        home.add_connection("north", street); street.add_connection("south", home); street.add_connection("east", mart); street.add_connection("north", square)
        mart.add_connection("west", street); square.add_connection("south", street); square.add_connection("west", hospital); square.add_connection("east", police); square.add_connection("north", tower)
        hospital.add_connection("east", square); police.add_connection("west", square); tower.add_connection("south", square)
        self.locations = [home, street, mart, square, hospital, police, tower]
        self.current_location = home
        
        # [修改] NPC 增加任务逻辑
        # 老王增加一个任务：清理丧尸
        trader = NPC("黑市老王", "戴墨镜的秃顶男人。", "黑市广场")
        trader.set_options(["看看货", "【任务】清理街道", "离开"]) # 选项1变成接任务
        
        dog = NPC("流浪狗旺财", "一只黄狗。", "废弃街道", item_needed="变异鼠肉"); dog.set_options(["给它肉吃", "赶走", "离开"])
        doc = NPC("陈医生", "被困医生。", "中心医院"); doc.set_options(["帮她解围", "无视"])
        self.npcs = [dog, doc, trader]
        
        self.item_db = {"过期罐头": {"hp": -5, "hunger": 30}, "变异鼠肉": {"hp": -20, "hunger": 60}, "压缩饼干": {"hp": 0, "hunger": 50}, "纯净水": {"hp": 5, "hunger": 10}, "急救包": {"hp": 60, "hunger": 0}, "警用手枪": {"hp":0,"hunger":0}, "霰弹枪": {"hp":0,"hunger":0}, "生锈铁管": {"hp":0,"hunger":0}}
        self.shop_items = {"压缩饼干": 20, "纯净水": 30, "急救包": 100, "警用手枪": 200, "霰弹枪": 500}
        
        # [新增] 任务定义库
        self.quest_db = {
            "clean_street": Quest("q1", "街道清理", "击杀 3 只丧尸", "kill_zombie", 3, 100, 50)
        }

    def update_display(self):
        time_str = self.get_time_desc()[0]
        self.gui.update_main_text(f"\n--- {self.current_location.name} ---\n{self.current_location.description}\n")
        self.gui.update_stats(self.player, f"{self.time_hour}:00 ({time_str})")
        self.gui.update_map(self.render_map())

    # (handle_input 同 v2.1)
    def handle_input(self, cmd):
        if self.current_enemy and not self.current_enemy.is_alive(): self.current_enemy = None
        if not self.player.is_alive: self.gui.show_death_screen(); return
        if self.current_enemy:
            if cmd not in ["attack", "run"]: self.gui.append_text("战斗中！", "red")
            return
        if self.current_npc:
            if self.current_npc.is_recruited: self.current_npc = None
            else: self.gui.append_text("请先完成对话。", "yellow"); return
        parts = cmd.lower().split()
        if not parts: return
        action = parts[0]
        if action == "go":
            direction = parts[1] if len(parts)>1 else ""
            if direction in self.current_location.connections:
                self.pass_time(1); self.current_location = self.current_location.connections[direction]; self.player.move()
                if not self.player.is_alive: self.gui.show_death_screen(); return
                if self.current_location.name == "广播塔": self.trigger_boss_fight(); return
                if self.check_npc_event(): return
                if self.check_encounter(0.4): return
                self.update_display()
            else: self.gui.append_text("无路可走。", "gray")
        elif action == "search":
            self.pass_time(1); self.player.search()
            if self.current_location.items:
                i = self.current_location.items.pop(0); self.player.get_item(i); self.gui.append_text(f"获得: {i}", "green")
                caps = random.randint(5,20); self.player.change_caps(caps); self.gui.append_text(f"发现 ${caps}", "gold")
                if self.player.gain_xp(10): self.gui.append_text("🆙 升级！", "cyan")
            else: self.gui.append_text("没东西。", "gray")
            self.update_display()
        elif action == "look": self.update_display()

    def handle_dialogue(self, i):
        npc = self.current_npc
        if not npc: return
        
        if npc.name == "黑市老王":
            if i == 0: self.gui.open_shop_window("老王的黑店", self.shop_items)
            elif i == 1: 
                # [新增] 接任务逻辑
                q = self.quest_db["clean_street"]
                if q not in self.player.active_quests and not q.is_completed:
                    q.is_accepted = True
                    self.player.active_quests.append(q)
                    self.gui.append_text(f"【任务接取】{q.title}: {q.description}", "cyan")
                    # 自动切到任务标签页提醒玩家
                    self.gui.tabs.select(self.gui.tab_quest)
                else:
                    self.gui.append_text("老王: 暂时没别的活儿了。", "gray")
                self.end_dialogue()
            elif i == 2: self.end_dialogue()
        
        # (保留其他 NPC)
        elif npc.name == "流浪狗旺财":
            if i==0:
                if "变异鼠肉" in self.player.inventory: self.player.remove_item("变异鼠肉"); self.recruit_npc(npc)
                elif "过期罐头" in self.player.inventory: self.player.remove_item("过期罐头"); self.recruit_npc(npc)
                else: self.gui.append_text("没有食物。", "gray"); self.end_dialogue()
            elif i==1: self.gui.append_text("赶走了。", "gray"); npc.location_name="None"; self.end_dialogue()
            elif i==2: self.end_dialogue()
        elif npc.name == "陈医生":
            if i==0:
                self.gui.append_text("开战！", "red"); self.current_enemy = Enemy("尸群", 80, 15, "..", []); self.gui.switch_mode("combat")
            elif i==1: self.gui.append_text("离开了。", "gray"); npc.location_name="None"; self.end_dialogue()

    def handle_combat(self, action):
        if not self.current_enemy: return
        if action == "attack":
            dmg = self.player.get_attack_damage()
            if "流浪狗旺财" in self.player.companions: self.gui.append_text("旺财协助!", "pink")
            if "陈医生" in self.player.companions: self.player.restore(hp=5); self.gui.append_text("陈医生治疗+5", "pink")
            crit = random.random()>0.8; 
            if crit: dmg*=2
            self.current_enemy.hp -= dmg
            self.gui.append_text(f"造成 {dmg} 伤害" + ("(暴击!)" if crit else ""), "yellow")
            
            if not self.current_enemy.is_alive():
                xp = 50
                self.gui.append_text(f"胜利! +{xp}XP", "green")
                caps = random.randint(10,50); self.player.change_caps(caps); self.gui.append_text(f"获得 ${caps}", "gold")
                if self.player.gain_xp(xp): self.gui.append_text("🆙 升级!", "cyan")
                
                # [新增] 检查任务进度：击杀丧尸
                if self.current_enemy.name == "丧尸":
                    completed = self.player.check_quests("kill_zombie")
                    for q in completed:
                        self.gui.append_text(f"🏆 任务完成: {q.title}", "cyan")
                        self.gui.append_text(f"奖励: {q.reward_xp}XP, ${q.reward_caps}", "gold")
                        self.player.gain_xp(q.reward_xp)
                        self.player.change_caps(q.reward_caps)
                        self.gui.tabs.select(self.gui.tab_quest) # 提示看任务页

                dead = self.current_enemy; self.current_enemy = None
                if dead.name == "变异暴君": self.trigger_win(); return
                if self.current_npc and self.current_npc.name == "陈医生": self.recruit_npc(self.current_npc); return
                for i in dead.loot: self.player.get_item(i)
                self.gui.switch_mode("exploration"); self.update_display(); return

            pdmg = self.current_enemy.damage; self.player.take_damage(pdmg)
            self.gui.append_text(f"受伤 -{pdmg}", "red"); self.gui.screen_flash("#330000")
            self.gui.update_stats(self.player, f"{self.time_hour}:00")
            if not self.player.is_alive: self.gui.show_death_screen()
        elif action == "run":
            if self.current_enemy.name == "变异暴君" or self.current_npc: self.gui.append_text("无法逃跑!", "red"); return
            if random.random()>0.5: self.current_enemy=None; self.gui.switch_mode("exploration"); self.update_display(); self.gui.append_text("逃跑成功", "green")
            else: self.gui.append_text("逃跑失败", "red"); self.player.take_damage(10); self.gui.update_stats(self.player, f"{self.time_hour}:00")

    # (保留其他所有方法，buy_item, gamble, check_encounter 等)
    def buy_item(self, n, p):
        if self.player.caps >= p: self.player.change_caps(-p); self.player.get_item(n); self.gui.append_text(f"购买 {n}", "green"); self.update_display()
        else: self.gui.append_text("钱不够!", "red")
    def gamble(self, a):
        if self.player.caps<a: self.gui.append_text("没钱!", "red"); return
        self.player.change_caps(-a)
        if random.random()>0.5: w=a*2; self.player.change_caps(w); self.gui.append_text(f"赢了! ${w}", "gold")
        else: self.gui.append_text("输了...", "gray")
        self.update_display()
    
    def check_encounter(self, chance):
        if self.current_location.name in ["地下避难所", "黑市广场"]: return False
        if random.random() < chance:
            boost = (self.player.level - 1) * 15
            e = random.choice([Enemy("丧尸", 40+boost, 10+boost, "..", []), Enemy("夜魔", 80+boost, 20+boost, "..", [])])
            self.current_enemy = e; self.gui.switch_mode("combat"); self.gui.append_text(f"遭遇: {e.name}", "red"); return True
        return False
    
    def check_npc_event(self):
        for npc in self.npcs:
            if npc.location_name == self.current_location.name and not npc.is_recruited:
                self.current_npc = npc; self.gui.switch_mode("dialogue", npc.dialogue_options); self.gui.append_text(f"\n{npc.intro}\n", "yellow"); return True
        return False
    def recruit_npc(self, npc): self.player.companions.append(npc.name); npc.is_recruited=True; self.current_npc=None; self.gui.append_text(f"[{npc.name}] 加入!", "cyan"); self.gui.switch_mode("exploration"); self.update_display()
    def end_dialogue(self): self.current_npc=None; self.gui.switch_mode("exploration"); self.update_display()
    def try_use_item(self, i): 
        if i not in self.player.inventory: return
        fx=self.item_db.get(i); 
        if fx["hp"]==0 and fx["hunger"]==0: self.gui.append_text("已装备", "gray"); return
        self.player.restore(fx["hp"], fx["hunger"]); self.player.remove_item(i); self.gui.append_text(f"使用了{i}", "green"); self.update_display()
    def get_time_desc(self): return ("白天", "gray") if 6<=self.time_hour<18 else ("深夜", "red")
    def pass_time(self, h): self.time_hour=(self.time_hour+h)%24
    def render_map(self): 
        grid = [[' . ' for _ in range(5)] for _ in range(5)]
        for loc in self.locations: grid[loc.y][loc.x] = f" {loc.icon} "
        grid[self.current_location.y][self.current_location.x] = " 😶 "
        return "".join(["".join(r)+"\n\n" for r in grid])
    def trigger_boss_fight(self): hp=300+self.player.level*50; self.current_enemy=Enemy("变异暴君", hp, 25+self.player.level*2, "..", []); self.gui.switch_mode("combat"); self.gui.append_text(f"BOSS战! HP:{hp}", "red")
    def trigger_win(self): self.gui.append_text("=== 通关! ===", "green"); self.player.is_alive=False; self.gui.control_panel.destroy()