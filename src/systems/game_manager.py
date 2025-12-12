# 文件路径: WastelandSurvival/src/systems/game_manager.py
from src.utils.data_manager import DataManager
from src.views.main_window import MainWindow
from src.models.player import Player
from src.models.location import Location
from src.models.enemy import Enemy
from src.models.npc import NPC
from src.models.quest import Quest
from src.data.narrative import TRAVEL_EVENTS, MORAL_EVENTS # [新增] 导入文案
import random

class GameManager:
    def __init__(self):
        self.data_mgr = DataManager()
        self.gui = MainWindow(self)
        self.pending_moral_event = None # 暂存当前的道德抉择
    
    def start(self): self.gui.start()

    # ... (start_new_game, load_game, save_game, return_to_menu, setup_world 保持 v2.3 不变) ...
    # 为节省篇幅，请保留 v2.3 的这部分代码，只要确保 setup_world 里引用了新的 Location 类即可
    def start_new_game(self):
        self.setup_world()
        self.player = Player("Survivor")
        self.time_hour = 8
        self.current_enemy = None; self.current_npc = None
        self.gui.show_game_interface()
        self.gui.append_text("=== 序章：废土苏醒 ===", "green")
        self.gui.append_text("你在避难所冰冷的地板上醒来。资源耗尽的警报声是你听到的第一个声音。\n即使外面是地狱，你也必须走出去了。\n", "normal")
        self.update_display()
    
    def load_game(self):
        data = self.data_mgr.load_game()
        if not data: return
        self.setup_world()
        p = data["player"]
        self.player = Player(p["name"])
        self.player.hp=p["hp"]; self.player.max_hp=p["max_hp"]; self.player.hunger=p["hunger"]
        self.player.inventory=p["inventory"]; self.player.companions=p["companions"]
        self.player.xp=p.get("xp",0); self.player.level=p.get("level",1); self.player.caps=p.get("caps",0)
        t_loc = data["game"]["location"]
        for loc in self.locations:
            if loc.name == t_loc: self.current_location = loc; break
        self.time_hour = data["game"]["time"]
        self.current_enemy = None; self.current_npc = None
        self.gui.show_game_interface()
        self.gui.append_text("=== 记忆读取完毕 ===", "gold")
        self.update_display()

    def save_game(self):
        if self.current_enemy: self.gui.append_text(">> 肾上腺素飙升中，无法冷静记录！", "red"); return
        if self.data_mgr.save_game(self.player, self.current_location.name, self.time_hour): self.gui.append_text(">> 这一刻被永久铭记。", "green")
    def return_to_menu(self): self.gui.show_main_menu()
    
    def setup_world(self):
        # ... (完全复制 v2.3 的 setup_world 代码) ...
        # 这里必须完整保留，否则会报错
        home = Location("地下避难所", "", 3, 5, "[🏠]")
        street = Location("废弃街道", "", 3, 4, "[🛣️]", items=["生锈铁管", "变异鼠肉"])
        square = Location("黑市广场", "", 3, 3, "[💰]", items=["过期罐头"])
        tower = Location("广播塔", "", 3, 1, "[💀]")
        mart = Location("沃尔玛超市", "", 4, 4, "[🛒]", items=["压缩饼干", "纯净水"])
        police = Location("警察局", "", 4, 3, "[👮]", items=["警用手枪", "霰弹枪"])
        hospital = Location("中心医院", "", 2, 3, "[🏥]", items=["急救包"])
        forest = Location("黑暗森林", "", 1, 3, "[🌲]", items=["草药", "毒蘑菇"])
        cave = Location("变异巢穴", "", 0, 3, "[🕸️]")
        factory = Location("废弃工厂", "", 5, 3, "[🏭]", items=["机械零件", "钢板"])
        lab = Location("秘密实验室", "", 6, 3, "[☢️]")

        home.add_connection("north", street); street.add_connection("south", home)
        street.add_connection("north", square); square.add_connection("south", street)
        square.add_connection("north", tower); tower.add_connection("south", square)
        hospital.add_connection("east", square); square.add_connection("west", hospital)
        square.add_connection("east", police); police.add_connection("west", square)
        street.add_connection("east", mart); mart.add_connection("west", street)
        hospital.add_connection("west", forest); forest.add_connection("east", hospital)
        forest.add_connection("west", cave); cave.add_connection("east", forest)
        police.add_connection("east", factory); factory.add_connection("west", police)
        factory.add_connection("east", lab); lab.add_connection("west", factory)

        self.locations = [home, street, square, tower, mart, police, hospital, forest, cave, factory, lab]
        self.current_location = home
        
        dog = NPC("流浪狗旺财", "一只瘦骨嶙峋的黄狗，眼神中充满了对食物的渴望。", "废弃街道", item_needed="变异鼠肉")
        dog.set_options(["分给它一点食物", "大声呵斥赶走它", "默默离开"])
        doc = NPC("陈医生", "被困在柜台后的医生，手术刀在颤抖。", "中心医院")
        doc.set_options(["冲上去解围 (战斗)", "冷漠地旁观"])
        trader = NPC("黑市老王", "戴墨镜的秃顶男人，在这个地狱里混得风生水起。", "黑市广场")
        trader.set_options(["交易物资", "【任务】清理街道", "离开"])
        engineer = NPC("老技工", "浑身油污，正在试图修复旧时代的荣光。", "废弃工厂")
        engineer.set_options(["【合成】动力臂", "闲聊", "离开"])
        self.npcs = [dog, doc, trader, engineer]
        
        self.item_db = {"过期罐头": {"hp": -5, "hunger": 30}, "变异鼠肉": {"hp": -20, "hunger": 60}, "压缩饼干": {"hp": 0, "hunger": 50}, "纯净水": {"hp": 5, "hunger": 10}, "急救包": {"hp": 60, "hunger": 0}, "草药": {"hp": 20, "hunger": 0}, "警用手枪": {"hp":0,"hunger":0}, "霰弹枪": {"hp":0,"hunger":0}, "生锈铁管": {"hp":0,"hunger":0}, "机械零件": {"hp":0,"hunger":0}, "钢板": {"hp":0,"hunger":0}, "动力臂": {"hp":0,"hunger":0}}
        self.shop_items = {"压缩饼干": 20, "纯净水": 30, "急救包": 100, "警用手枪": 200, "霰弹枪": 500}
        self.quest_db = {"clean_street": Quest("q1", "街道清理", "击杀 3 只丧尸", "kill_zombie", 3, 100, 50)}

    def update_display(self):
        time_str = self.get_time_desc()[0]
        # [修改] 使用新的富文本描述
        desc = self.current_location.get_info()
        self.gui.update_main_text(f"\n--- {self.current_location.name} ---\n{desc}\n")
        self.gui.update_stats(self.player, f"{self.time_hour}:00 ({time_str})")
        
        grid_data = self.get_map_grid()
        player_pos = (self.current_location.x, self.current_location.y)
        self.gui.update_map(grid_data, player_pos)

    def get_map_grid(self):
        grid = [[None for _ in range(7)] for _ in range(7)]
        for loc in self.locations:
            if 0 <= loc.x < 7 and 0 <= loc.y < 7: grid[loc.y][loc.x] = loc
        return grid

    # === [修改] 移动逻辑：加入随机叙事 ===
    def handle_input(self, cmd):
        if self.current_enemy and not self.current_enemy.is_alive(): self.current_enemy = None
        if not self.player.is_alive: self.gui.show_death_screen(); return
        if self.current_enemy:
            if cmd not in ["attack", "run"]: self.gui.append_text(">> 肾上腺素激增！现在不是做这个的时候！(请攻击或逃跑)", "red")
            return
        if self.current_npc:
            if self.current_npc.is_recruited: self.current_npc = None
            else: self.gui.append_text(">> 对方正在等待你的回应。", "yellow"); return

        parts = cmd.lower().split()
        if not parts: return
        action = parts[0]

        if action == "go":
            direction = parts[1] if len(parts)>1 else ""
            if direction in self.current_location.connections:
                self.pass_time(1)
                self.current_location = self.current_location.connections[direction]
                self.player.move()
                
                if not self.player.is_alive: self.gui.show_death_screen(); return
                
                # [新增] 20% 概率触发环境叙事 (增加氛围)
                if random.random() < 0.2:
                    event_text = random.choice(TRAVEL_EVENTS)
                    self.gui.append_text(f"【旅途见闻】{event_text}", "gray")

                if self.current_location.name == "广播塔": self.trigger_boss_fight(); return
                if self.check_npc_event(): return
                if self.check_encounter(0.4): return
                self.update_display()
            else: self.gui.append_text("前方是一片死路，或者被废墟堵死了。", "gray")

        # === [修改] 搜刮逻辑：加入道德抉择 ===
        elif action == "search":
            self.pass_time(1); self.player.search()
            
            # 10% 概率触发道德事件 (仅在没有搜到东西时)
            if not self.current_location.items and random.random() < 0.15:
                event = random.choice(MORAL_EVENTS)
                self.pending_moral_event = event # 暂存事件
                self.gui.append_text(f"\n>> {event['desc']}", "yellow")
                # 借用对话模式的 UI 来显示选项
                self.gui.switch_mode("dialogue", [event['opt1'], event['opt2']])
                return

            if self.current_location.items:
                i = self.current_location.items.pop(0); self.player.get_item(i); self.gui.append_text(f"你在废墟中翻找... 发现了: [{i}]", "green")
                caps = random.randint(5,20); self.player.change_caps(caps); self.gui.append_text(f"还在角落找到了 ${caps}", "gold")
                if self.player.gain_xp(10): self.gui.append_text("🆙 生存经验提升！", "cyan")
            else: self.gui.append_text("你翻遍了周围，除了灰尘什么也没找到。", "gray")
            self.update_display()
        
        elif action == "look": self.update_display()

    # === [修改] 对话处理：兼容道德抉择 ===
    def handle_dialogue(self, i):
        # 优先处理道德抉择
        if self.pending_moral_event:
            evt = self.pending_moral_event
            res = evt[f"res{i+1}"]
            
            self.gui.append_text(f"> {res['msg']}", "white")
            if "item" in res: self.player.get_item(res["item"]); self.gui.append_text(f"获得: {res['item']}", "green")
            if "hp" in res: self.player.take_damage(-res["hp"]); self.gui.append_text(f"HP {res['hp']}", "red")
            if "xp" in res: self.player.gain_xp(res["xp"]); self.gui.append_text(f"XP +{res['xp']}", "cyan")
            
            self.pending_moral_event = None
            self.gui.switch_mode("exploration")
            self.update_display()
            return

        npc = self.current_npc
        if not npc: return
        # (NPC 逻辑保持 v2.3 不变)
        if npc.name == "老技工":
            if i == 0:
                if "机械零件" in self.player.inventory and "钢板" in self.player.inventory:
                    self.player.remove_item("机械零件"); self.player.remove_item("钢板"); self.player.get_item("动力臂")
                    self.gui.append_text("老技工一阵敲打... 获得了 [动力臂] (攻击+30)！", "cyan"); self.gui.screen_flash("#00ffff", 200)
                elif "动力臂" in self.player.inventory: self.gui.append_text("你已经有这个装备了。", "gray")
                else: self.gui.append_text("材料不足！需要 [机械零件] 和 [钢板]。", "red")
            elif i == 1: self.gui.append_text("老技工: 东边的实验室很危险...", "yellow")
            elif i == 2: self.end_dialogue()
        elif npc.name == "黑市老王":
            if i == 0: self.gui.open_shop_window("老王的黑店", self.shop_items)
            elif i == 1: 
                q = self.quest_db["clean_street"]
                if q not in self.player.active_quests and not q.is_completed:
                    q.is_accepted = True; self.player.active_quests.append(q); self.gui.append_text(f"接取: {q.title}", "cyan"); self.gui.tabs.select(self.gui.tab_quest)
                else: self.gui.append_text("没活了。", "gray")
                self.end_dialogue()
            elif i == 2: self.end_dialogue()
        elif npc.name == "流浪狗旺财":
            if i==0:
                if "变异鼠肉" in self.player.inventory: self.player.remove_item("变异鼠肉"); self.recruit_npc(npc)
                elif "过期罐头" in self.player.inventory: self.player.remove_item("过期罐头"); self.recruit_npc(npc)
                else: self.gui.append_text("你摸遍了口袋，没有食物...", "gray"); self.end_dialogue()
            elif i==1: self.gui.append_text("你狠心地赶走了它。", "gray"); npc.location_name="None"; self.end_dialogue()
            elif i==2: self.end_dialogue()
        elif npc.name == "陈医生":
            if i==0: self.gui.append_text("你怒吼一声冲了上去！", "red"); self.current_enemy = Enemy("尸群", 80, 15, "..", []); self.gui.switch_mode("combat")
            elif i==1: self.gui.append_text("你选择了冷眼旁观。", "gray"); npc.location_name="None"; self.end_dialogue()

    # (其他逻辑保持 v2.3 原样：handle_combat, check_encounter 等)
    def handle_combat(self, action):
        if not self.current_enemy: return
        if action == "attack":
            dmg = self.player.get_attack_damage()
            if "动力臂" in self.player.inventory: self.gui.append_text("动力臂充能重击!", "cyan")
            if "流浪狗旺财" in self.player.companions: self.gui.append_text("旺财协助撕咬!", "pink")
            if "陈医生" in self.player.companions: self.player.restore(hp=5); self.gui.append_text("陈医生紧急包扎+5", "pink")
            crit = random.random()>0.8; 
            if crit: dmg*=2
            self.current_enemy.hp -= dmg
            self.gui.append_text(f"你造成了 {dmg} 点伤害" + (" (暴击!)" if crit else ""), "yellow")
            if not self.current_enemy.is_alive():
                xp = 50
                if self.current_enemy.name == "变异巨熊": xp = 150
                self.gui.append_text(f"敌人倒下了! +{xp}XP", "green")
                caps = random.randint(10,50); self.player.change_caps(caps); self.gui.append_text(f"搜刮获得 ${caps}", "gold")
                if self.player.gain_xp(xp): self.gui.append_text("🆙 能力提升！", "cyan")
                if self.current_enemy.name == "丧尸":
                    completed = self.player.check_quests("kill_zombie")
                    for q in completed: self.gui.append_text(f"任务完成: {q.title}", "cyan"); self.player.gain_xp(q.reward_xp); self.player.change_caps(q.reward_caps)
                dead = self.current_enemy; self.current_enemy = None
                if dead.name == "变异暴君": self.trigger_win(); return
                if self.current_npc and self.current_npc.name == "陈医生": self.recruit_npc(self.current_npc); return
                for i in dead.loot: self.player.get_item(i)
                self.gui.switch_mode("exploration"); self.update_display(); return
            pdmg = self.current_enemy.damage; self.player.take_damage(pdmg)
            self.gui.append_text(f"受到反击! HP -{pdmg}", "red"); self.gui.screen_flash("#330000")
            self.gui.update_stats(self.player, f"{self.time_hour}:00")
            if not self.player.is_alive: self.gui.show_death_screen()
        elif action == "run":
            if self.current_enemy.name == "变异暴君" or self.current_npc: self.gui.append_text("这种情况下无法逃跑!", "red"); return
            if random.random()>0.5: self.current_enemy=None; self.gui.switch_mode("exploration"); self.update_display(); self.gui.append_text("你狼狈地逃脱了。", "green")
            else: self.gui.append_text("逃跑失败，被绊倒了！", "red"); self.player.take_damage(10); self.gui.update_stats(self.player, f"{self.time_hour}:00")

    def check_encounter(self, chance):
        if self.current_location.name in ["地下避难所", "黑市广场", "废弃工厂"]: return False
        if random.random() < chance:
            boost = (self.player.level - 1) * 15
            if "森林" in self.current_location.name: e = Enemy("变异巨熊", 120+boost, 30+boost, "..", ["草药"])
            elif "实验室" in self.current_location.name: e = Enemy("失控机甲", 100+boost, 25+boost, "..", ["机械零件"])
            else: e = random.choice([Enemy("丧尸", 40+boost, 10+boost, "..", []), Enemy("夜魔", 80+boost, 20+boost, "..", [])])
            self.current_enemy = e; self.gui.switch_mode("combat"); self.gui.append_text(f"⚠ 遭遇强敌: {e.name}", "red"); return True
        return False
    
    def check_npc_event(self):
        for npc in self.npcs:
            if npc.location_name == self.current_location.name and not npc.is_recruited:
                self.current_npc = npc; self.gui.switch_mode("dialogue", npc.dialogue_options); self.gui.append_text(f"\n{npc.intro}\n", "yellow"); return True
        return False
    def recruit_npc(self, npc): self.player.companions.append(npc.name); npc.is_recruited=True; self.current_npc=None; self.gui.append_text(f"[{npc.name}] 决定跟随你！", "cyan"); self.gui.switch_mode("exploration"); self.update_display()
    def end_dialogue(self): self.current_npc=None; self.gui.switch_mode("exploration"); self.update_display()
    def try_use_item(self, i): 
        if i not in self.player.inventory: return
        fx=self.item_db.get(i); 
        if fx["hp"]==0 and fx["hunger"]==0: self.gui.append_text("这是一个装备物品。", "gray"); return
        self.player.restore(fx["hp"], fx["hunger"]); self.player.remove_item(i); self.gui.append_text(f"使用了{i}，状态恢复。", "green"); self.update_display()
    def buy_item(self, n, p):
        if self.player.caps >= p: self.player.change_caps(-p); self.player.get_item(n); self.gui.append_text(f"交易成功: {n}", "green"); self.update_display()
        else: self.gui.append_text("瓶盖不足。", "red")
    def gamble(self, a):
        if self.player.caps<a: self.gui.append_text("你的瓶盖不够。", "red"); return
        self.player.change_caps(-a)
        if random.random()>0.5: w=a*2; self.player.change_caps(w); self.gui.append_text(f"手气不错! 赢得了 ${w}", "gold")
        else: self.gui.append_text("真倒霉，输光了。", "gray")
        self.update_display()
    def get_time_desc(self): return ("白天", "gray") if 6<=self.time_hour<18 else ("深夜", "red")
    def pass_time(self, h): self.time_hour=(self.time_hour+h)%24
    def render_map(self): 
        grid = [[' . ' for _ in range(7)] for _ in range(7)]
        for loc in self.locations: grid[loc.y][loc.x] = f" {loc.icon} "
        grid[self.current_location.y][self.current_location.x] = " 😶 "
        return "".join(["".join(r)+"\n\n" for r in grid])
    def trigger_boss_fight(self): hp=300+self.player.level*50; self.current_enemy=Enemy("变异暴君", hp, 25+self.player.level*2, "..", []); self.gui.switch_mode("combat"); self.gui.append_text(f"⚠ 警报：检测到暴君级生物! HP:{hp}", "red")
    def trigger_win(self): self.gui.append_text("=== 任务完成：新世界的黎明 ===", "green"); self.player.is_alive=False; self.gui.control_panel.destroy()