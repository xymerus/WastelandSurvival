# 文件路径: WastelandSurvival/src/systems/game_manager.py
from src.utils.data_manager import DataManager
from src.views.main_window import MainWindow
from src.models.player import Player
from src.models.location import Location
from src.models.enemy import Enemy
from src.models.npc import NPC
from src.models.quest import Quest
import random

class GameManager:
    def __init__(self):
        self.data_mgr = DataManager()
        self.gui = MainWindow(self)
    
    def start(self): self.gui.start()

    def start_new_game(self):
        self.setup_world()
        self.player = Player("Survivor")
        self.time_hour = 8
        self.current_enemy = None; self.current_npc = None
        self.gui.show_game_interface()
        self.gui.append_text("=== v2.3 荒野版启动 ===", "green")
        self.update_display()
    
    def load_game(self):
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

    def save_game(self):
        if self.current_enemy: self.gui.append_text("战斗中不可存档!", "red"); return
        if self.data_mgr.save_game(self.player, self.current_location.name, self.time_hour): self.gui.append_text("进度已保存", "green")
    def return_to_menu(self): self.gui.show_main_menu()

    def setup_world(self):
        # === 7x7 地图构建 ===
        # 中心区 (x=3, y=3 是中心点)
        home = Location("地下避难所", "你的安全屋。", 3, 5, "[🏠]")
        street = Location("废弃街道", "连接城市的要道。", 3, 4, "[🛣️]", items=["生锈铁管", "变异鼠肉"])
        square = Location("黑市广场", "流浪者聚集地。", 3, 3, "[💰]", items=["过期罐头"])
        tower = Location("广播塔", "最终决战之地。", 3, 1, "[💀]")
        
        # 城市设施
        mart = Location("沃尔玛超市", "废弃超市。", 4, 4, "[🛒]", items=["压缩饼干", "纯净水"])
        police = Location("警察局", "曾经的防线。", 4, 3, "[👮]", items=["警用手枪", "霰弹枪"])
        hospital = Location("中心医院", "充满消毒水味。", 2, 3, "[🏥]", items=["急救包"])
        
        # [新增] 西部荒野
        forest = Location("黑暗森林", "树木扭曲，野兽出没。", 1, 3, "[🌲]", items=["草药", "毒蘑菇"])
        cave = Location("变异巢穴", "阴森的洞穴，传来低吼。", 0, 3, "[🕸️]") # 强敌点
        
        # [新增] 东部工业区
        factory = Location("废弃工厂", "充满机油味，巨大的齿轮还在转动。", 5, 3, "[🏭]", items=["机械零件", "钢板"])
        lab = Location("秘密实验室", "大门紧锁，写着'生化危险'。", 6, 3, "[☢️]")

        # 建立连接 (手动拓扑)
        # 南北主干道
        home.add_connection("north", street); street.add_connection("south", home)
        street.add_connection("north", square); square.add_connection("south", street)
        square.add_connection("north", tower); tower.add_connection("south", square)
        
        # 东西主干道 (医院 <-> 广场 <-> 警局)
        hospital.add_connection("east", square); square.add_connection("west", hospital)
        square.add_connection("east", police); police.add_connection("west", square)
        
        # 城市分支
        street.add_connection("east", mart); mart.add_connection("west", street)
        
        # [新增] 荒野连接
        # 医院 <-> 森林 <-> 巢穴
        hospital.add_connection("west", forest); forest.add_connection("east", hospital)
        forest.add_connection("west", cave); cave.add_connection("east", forest)
        
        # 警局 <-> 工厂 <-> 实验室
        police.add_connection("east", factory); factory.add_connection("west", police)
        factory.add_connection("east", lab); lab.add_connection("west", factory)

        self.locations = [home, street, square, tower, mart, police, hospital, forest, cave, factory, lab]
        self.current_location = home
        
        # === NPC ===
        dog = NPC("流浪狗旺财", "一只黄狗。", "废弃街道", item_needed="变异鼠肉")
        dog.set_options(["给它肉吃", "赶走", "离开"])
        
        doc = NPC("陈医生", "被困医生。", "中心医院")
        doc.set_options(["帮她解围", "无视"])
        
        trader = NPC("黑市老王", "戴墨镜的秃顶男人。", "黑市广场")
        trader.set_options(["看看货", "【任务】清理街道", "离开"])
        
        # [新增] 工程师
        engineer = NPC("老技工", "浑身油污的老头，正在敲打一台机器。", "废弃工厂")
        engineer.set_options(["【合成】动力臂 (需机械零件+钢板)", "闲聊", "离开"])

        self.npcs = [dog, doc, trader, engineer]
        
        # 物品与任务
        self.item_db = {
            "过期罐头": {"hp": -5, "hunger": 30}, "变异鼠肉": {"hp": -20, "hunger": 60},
            "压缩饼干": {"hp": 0, "hunger": 50}, "纯净水": {"hp": 5, "hunger": 10},
            "急救包": {"hp": 60, "hunger": 0}, "草药": {"hp": 20, "hunger": 0},
            "警用手枪": {"hp":0,"hunger":0}, "霰弹枪": {"hp":0,"hunger":0}, 
            "生锈铁管": {"hp":0,"hunger":0}, "机械零件": {"hp":0,"hunger":0},
            "钢板": {"hp":0,"hunger":0}, "动力臂": {"hp":0,"hunger":0} # 强力装备
        }
        self.shop_items = {"压缩饼干": 20, "纯净水": 30, "急救包": 100, "警用手枪": 200, "霰弹枪": 500}
        self.quest_db = {"clean_street": Quest("q1", "街道清理", "击杀 3 只丧尸", "kill_zombie", 3, 100, 50)}

    def update_display(self):
        time_str = self.get_time_desc()[0]
        self.gui.update_main_text(f"\n--- {self.current_location.name} ---\n{self.current_location.description}\n")
        self.gui.update_stats(self.player, f"{self.time_hour}:00 ({time_str})")
        self.gui.update_map(self.render_map())

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
        
        if npc.name == "老技工":
            if i == 0: # 合成动力臂
                if "机械零件" in self.player.inventory and "钢板" in self.player.inventory:
                    self.player.remove_item("机械零件")
                    self.player.remove_item("钢板")
                    self.player.get_item("动力臂")
                    self.gui.append_text("老技工一阵敲打... 获得了 [动力臂] (攻击+30)！", "cyan")
                    self.gui.screen_flash("#00ffff", 200)
                elif "动力臂" in self.player.inventory:
                    self.gui.append_text("你已经有这个装备了。", "gray")
                else:
                    self.gui.append_text("材料不足！需要 [机械零件] 和 [钢板]。", "red")
            elif i == 1: self.gui.append_text("老技工: 东边的实验室很危险...", "yellow")
            elif i == 2: self.end_dialogue()
            
        elif npc.name == "黑市老王":
            if i == 0: self.gui.open_shop_window("老王的黑店", self.shop_items)
            elif i == 1: 
                q = self.quest_db["clean_street"]
                if q not in self.player.active_quests and not q.is_completed:
                    q.is_accepted = True; self.player.active_quests.append(q)
                    self.gui.append_text(f"【任务】{q.title}", "cyan"); self.gui.tabs.select(self.gui.tab_quest)
                else: self.gui.append_text("没活了。", "gray")
                self.end_dialogue()
            elif i == 2: self.end_dialogue()
        
        # (保留其他 NPC 逻辑: 旺财, 陈医生)
        elif npc.name == "流浪狗旺财":
            if i==0:
                if "变异鼠肉" in self.player.inventory: self.player.remove_item("变异鼠肉"); self.recruit_npc(npc)
                elif "过期罐头" in self.player.inventory: self.player.remove_item("过期罐头"); self.recruit_npc(npc)
                else: self.gui.append_text("没有食物。", "gray"); self.end_dialogue()
            elif i==1: self.gui.append_text("赶走了。", "gray"); npc.location_name="None"; self.end_dialogue()
            elif i==2: self.end_dialogue()
        elif npc.name == "陈医生":
            if i==0: self.gui.append_text("开战！", "red"); self.current_enemy = Enemy("尸群", 80, 15, "..", []); self.gui.switch_mode("combat")
            elif i==1: self.gui.append_text("离开了。", "gray"); npc.location_name="None"; self.end_dialogue()

    def handle_combat(self, action):
        if not self.current_enemy: return
        if action == "attack":
            dmg = self.player.get_attack_damage()
            # [新增] 动力臂加成 (需要去 Player 类加逻辑，这里仅做 UI 提示)
            if "动力臂" in self.player.inventory: self.gui.append_text("动力臂充能重击!", "cyan")
            if "流浪狗旺财" in self.player.companions: self.gui.append_text("旺财协助!", "pink")
            if "陈医生" in self.player.companions: self.player.restore(hp=5); self.gui.append_text("陈医生治疗+5", "pink")
            
            crit = random.random()>0.8; 
            if crit: dmg*=2
            self.current_enemy.hp -= dmg
            self.gui.append_text(f"造成 {dmg} 伤害" + ("(暴击!)" if crit else ""), "yellow")
            
            if not self.current_enemy.is_alive():
                xp = 50
                if self.current_enemy.name == "变异巨熊": xp = 150 # [新增] 精英怪经验
                self.gui.append_text(f"胜利! +{xp}XP", "green")
                caps = random.randint(10,50); self.player.change_caps(caps); self.gui.append_text(f"获得 ${caps}", "gold")
                if self.player.gain_xp(xp): self.gui.append_text("🆙 升级!", "cyan")
                if self.current_enemy.name == "丧尸":
                    completed = self.player.check_quests("kill_zombie")
                    for q in completed:
                        self.gui.append_text(f"任务完成: {q.title}", "cyan"); self.player.gain_xp(q.reward_xp); self.player.change_caps(q.reward_caps)

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

    # [新增] 扩充遇敌列表
    def check_encounter(self, chance):
        if self.current_location.name in ["地下避难所", "黑市广场", "废弃工厂"]: return False # 安全区
        if random.random() < chance:
            boost = (self.player.level - 1) * 15
            # 不同区域不同怪
            if "森林" in self.current_location.name:
                e = Enemy("变异巨熊", 120+boost, 30+boost, "巨大的熊", ["草药"])
            elif "实验室" in self.current_location.name:
                e = Enemy("失控机甲", 100+boost, 25+boost, "暴走的机器人", ["机械零件"])
            else:
                e = random.choice([Enemy("丧尸", 40+boost, 10+boost, "..", []), Enemy("夜魔", 80+boost, 20+boost, "..", [])])
            self.current_enemy = e; self.gui.switch_mode("combat"); self.gui.append_text(f"遭遇: {e.name}", "red"); return True
        return False
    
    # 渲染地图改为 7x7
    def render_map(self): 
        # 0-6
        grid = [[' . ' for _ in range(7)] for _ in range(7)]
        for loc in self.locations: grid[loc.y][loc.x] = f" {loc.icon} "
        grid[self.current_location.y][self.current_location.x] = " 😶 "
        return "".join(["".join(r)+"\n\n" for r in grid])

    # (保留其他所有方法)
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
    def buy_item(self, n, p):
        if self.player.caps >= p: self.player.change_caps(-p); self.player.get_item(n); self.gui.append_text(f"购买 {n}", "green"); self.update_display()
        else: self.gui.append_text("钱不够!", "red")
    def gamble(self, a):
        if self.player.caps<a: self.gui.append_text("没钱!", "red"); return
        self.player.change_caps(-a)
        if random.random()>0.5: w=a*2; self.player.change_caps(w); self.gui.append_text(f"赢了! ${w}", "gold")
        else: self.gui.append_text("输了...", "gray")
        self.update_display()
    def get_time_desc(self): return ("白天", "gray") if 6<=self.time_hour<18 else ("深夜", "red")
    def pass_time(self, h): self.time_hour=(self.time_hour+h)%24
    def trigger_boss_fight(self): hp=300+self.player.level*50; self.current_enemy=Enemy("变异暴君", hp, 25+self.player.level*2, "..", []); self.gui.switch_mode("combat"); self.gui.append_text(f"BOSS战! HP:{hp}", "red")
    def trigger_win(self): self.gui.append_text("=== 通关! ===", "green"); self.player.is_alive=False; self.gui.control_panel.destroy()