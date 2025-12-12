# 文件路径: WastelandSurvival/src/views/main_window.py
import tkinter as tk
from tkinter import ttk

class MainWindow:
    def __init__(self, game_manager):
        self.gm = game_manager
        self.root = tk.Tk()
        self.root.title(">>> 废土行者 v2.4 (战术地图版) <<<")
        self.root.geometry("1180x800")
        
        self.colors = {
            "bg": "#050505", "panel": "#141414", "text": "#e0e0e0",
            "highlight": "#33ff33", "danger": "#ff3333", "item": "#00ffff", 
            "story": "#ffcc00", "map_bg": "#000000", "gold": "#ffd700"
        }
        self.root.configure(bg=self.colors["bg"])
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("red.Horizontal.TProgressbar", foreground='red', background='#d10000', troughcolor='#300000', borderwidth=0)
        self.style.configure("green.Horizontal.TProgressbar", foreground='green', background='#00d100', troughcolor='#003000', borderwidth=0)
        self.style.configure("TNotebook", background=self.colors["bg"], borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#333", foreground="#aaa", padding=[12, 8], font=("Arial", 10))
        self.style.map("TNotebook.Tab", background=[("selected", "#444")], foreground=[("selected", "#fff")])

        self.current_frame = None
        self._bind_global_keys()
        self.show_main_menu()

    def _bind_global_keys(self): self.root.bind("<Return>", lambda e: self._on_enter())
    def _on_enter(self): 
        if hasattr(self, 'entry') and self.entry.winfo_exists():
            c=self.entry.get(); self.entry.delete(0,tk.END); self.gm.handle_input(c)

    # === 核心：配置地图颜色标签 ===
    def _setup_map_tags(self):
        # 定义不同地形的样式 (背景色 + 前景色)
        # 格式: (前景色, 背景色)
        styles = {
            "player":   ("white", "#d10000"), # 玩家：红底白字
            "home":     ("white", "#003366"), # 家：蓝底
            "forest":   ("#aaffaa", "#002200"), # 森林：深绿底
            "city":     ("#aaaaaa", "#222222"), # 城市：深灰底
            "danger":   ("#ff5555", "#440000"), # 危险：暗红底
            "special":  ("#ffff00", "#444400"), # 特殊：暗黄底
            "empty":    ("#333333", "#000000")  # 空地
        }
        for name, (fg, bg) in styles.items():
            self.map_area.tag_config(name, foreground=fg, background=bg, font=("Segoe UI Emoji", 12)) # 使用支持Emoji的字体

    # === [重写] 地图更新方法 ===
    def update_map(self, grid_data, player_pos):
        """
        grid_data: 7x7 的 Location 对象列表 (空的地方是 None)
        player_pos: (x, y) 元组
        """
        if not hasattr(self, 'map_area'): return
        
        self.map_area.config(state="normal")
        self.map_area.delete(1.0, tk.END)
        
        # 遍历 7x7 网格
        for y in range(7):
            line_tags = []
            for x in range(7):
                loc = grid_data[y][x]
                
                # 1. 判断是否是玩家位置
                if (x, y) == player_pos:
                    # 玩家覆盖在格子上
                    icon = " 🤠 " # 帅气的牛仔头
                    tag = "player"
                
                # 2. 判断是否有地点
                elif loc:
                    icon = f" {loc.icon} "
                    # 根据名字决定颜色风格
                    if "森林" in loc.name: tag = "forest"
                    elif "避难所" in loc.name: tag = "home"
                    elif "塔" in loc.name or "巢穴" in loc.name: tag = "danger"
                    elif "黑市" in loc.name: tag = "special"
                    else: tag = "city"
                
                # 3. 空地
                else:
                    icon = "  .  "
                    tag = "empty"
                
                # 插入文本并应用标签
                self.map_area.insert(tk.END, icon, tag)
                # 加个小间距
                self.map_area.insert(tk.END, " ") 
            
            self.map_area.insert(tk.END, "\n\n") # 双换行拉开纵向距离
            
        self.map_area.config(state="disabled")

    # ... (其余 UI 方法保持不变) ...
    def show_main_menu(self):
        self._clear_frame(); self.current_frame = tk.Frame(self.root, bg=self.colors["bg"]); self.current_frame.pack(fill="both", expand=True)
        tk.Label(self.current_frame, text="WASTELAND WALKER", font=("Impact", 60), bg=self.colors["bg"], fg=self.colors["highlight"]).pack(pady=(150, 20))
        btn = {"font": ("Arial", 14), "width": 20, "bg": "#222", "fg": "white", "bd": 0, "activebackground": "#444", "activeforeground": "white"}
        tk.Button(self.current_frame, text="⚡ 新 游 戏", command=self.gm.start_new_game, **btn).pack(pady=10)
        s = "normal" if self.gm.data_mgr.has_save_file() else "disabled"
        l_btn = btn.copy(); l_btn["fg"] = "white" if s=="normal" else "#444"
        tk.Button(self.current_frame, text="📂 继续游戏", command=self.gm.load_game, state=s, **l_btn).pack(pady=10)
        tk.Button(self.current_frame, text="❌ 退 出", command=self.root.quit, **btn).pack(pady=10)

    def show_game_interface(self):
        self._clear_frame(); self.current_frame = tk.Frame(self.root, bg=self.colors["bg"]); self.current_frame.pack(fill="both", expand=True)
        self._bind_game_keys()
        
        # 布局
        main_pad = tk.Frame(self.current_frame, bg=self.colors["bg"]); main_pad.pack(fill="both", expand=True, padx=20, pady=20)
        left_panel = tk.Frame(main_pad, bg=self.colors["panel"]); left_panel.pack(side="left", fill="both", expand=True)
        
        # HUD
        hud = tk.Frame(left_panel, bg=self.colors["panel"], height=50); hud.pack(fill="x", padx=15, pady=15)
        tk.Label(hud, text="HP", bg=self.colors["panel"], fg="red", font=("Arial",10,"bold")).pack(side="left")
        self.hp_bar = ttk.Progressbar(hud, style="red.Horizontal.TProgressbar", length=120, maximum=100); self.hp_bar.pack(side="left", padx=10)
        tk.Label(hud, text="AP", bg=self.colors["panel"], fg="#00ff00", font=("Arial",10,"bold")).pack(side="left", padx=(10,0))
        self.hunger_bar = ttk.Progressbar(hud, style="green.Horizontal.TProgressbar", length=120, maximum=100); self.hunger_bar.pack(side="left", padx=10)
        self.lvl_label = tk.Label(hud, text="Lv.1", bg=self.colors["panel"], fg="white", font=("Arial",10)); self.lvl_label.pack(side="left", padx=15)
        self.caps_label = tk.Label(hud, text="$ 50", bg=self.colors["panel"], fg=self.colors["gold"], font=("Arial",12,"bold")); self.caps_label.pack(side="right", padx=10)

        # 文本
        self.text_area = tk.Text(left_panel, bg="#080808", fg="#ccc", font=("Microsoft YaHei UI", 11), state="disabled", wrap="word", bd=0, padx=20, pady=20)
        self.text_area.pack(fill="both", expand=True)
        self._setup_tags()

        # 右侧
        right_panel = tk.Frame(main_pad, bg=self.colors["panel"], width=380) # 更宽
        right_panel.pack(side="right", fill="y", padx=(20,0)); right_panel.pack_propagate(False)
        self.tabs = ttk.Notebook(right_panel); self.tabs.pack(fill="both", expand=True)
        
        # Tab1 控制台
        self.tab_console = tk.Frame(self.tabs, bg=self.colors["panel"]); self.tabs.add(self.tab_console, text=" 战术视图 ")
        tk.Label(self.tab_console, text="RADAR SYSTEM ONLINE", bg=self.colors["panel"], fg="#444", font=("Arial",8)).pack(pady=(10,0))
        
        # 地图区域 (注意这里配置了 tag)
        self.map_area = tk.Text(self.tab_console, bg=self.colors["map_bg"], bd=0, width=35, height=16, state="disabled", cursor="cross")
        self.map_area.pack(pady=10, padx=10)
        self._setup_map_tags() # 应用地图颜色

        self.time_label = tk.Label(self.tab_console, text="--:--", bg=self.colors["panel"], fg="yellow", font=("Consolas", 16, "bold")); self.time_label.pack()
        self.control_panel = tk.Frame(self.tab_console, bg=self.colors["panel"]); self.control_panel.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab2 任务
        self.tab_quest = tk.Frame(self.tabs, bg=self.colors["panel"]); self.tabs.add(self.tab_quest, text=" 任务日志 ")
        self.quest_text = tk.Text(self.tab_quest, bg="#111", fg="#aaa", font=("Consolas", 10), state="disabled", bd=0, padx=15, pady=15); self.quest_text.pack(fill="both", expand=True)

        self.entry = tk.Entry(right_panel, bg="#222", fg="white", relief="flat", font=("Consolas", 12)); self.entry.pack(side="bottom", fill="x", padx=10, pady=10)

    # (保留其他辅助方法)
    def update_quest_log(self, quests):
        if not hasattr(self, 'quest_text'): return
        self.quest_text.config(state="normal"); self.quest_text.delete(1.0, tk.END)
        if not quests: self.quest_text.insert(tk.END, ">> 无活跃任务 <<\n\n请前往城市中心寻找线索。")
        else:
            for q in quests: self.quest_text.insert(tk.END, q.get_status_str() + "\n\n")
        self.quest_text.config(state="disabled")

    def update_stats(self, player, time_str):
        if hasattr(self, 'hp_bar'):
            self.hp_bar['value'] = (player.hp / player.max_hp) * 100
            self.hunger_bar['value'] = player.hunger
            self.lvl_label.config(text=f"Lv.{player.level}")
            self.caps_label.config(text=f"$ {player.caps}")
            self.time_label.config(text=time_str)
            self.update_quest_log(player.active_quests)

    def _clear_frame(self): 
        if self.current_frame: self.current_frame.destroy()
    def _bind_game_keys(self):
        self.root.bind("<w>", lambda e: self.gm.handle_input("go north"))
        self.root.bind("<s>", lambda e: self.gm.handle_input("go south"))
        self.root.bind("<a>", lambda e: self.gm.handle_input("go west"))
        self.root.bind("<d>", lambda e: self.gm.handle_input("go east"))
        self.root.bind("<space>", lambda e: self.gm.handle_input("search"))
    def switch_mode(self, mode, options=None):
        for w in self.control_panel.winfo_children(): w.destroy()
        if mode == "exploration": self._setup_exploration_ui()
        elif mode == "combat": self._setup_combat_ui()
        elif mode == "dialogue": self._setup_dialogue_ui(options)
    def _setup_exploration_ui(self):
        gf = tk.Frame(self.control_panel, bg=self.colors["panel"]); gf.pack(pady=5)
        cfg = {"width": 4, "bg": "#333", "fg": "white", "relief": "raised", "bd": 1}
        tk.Button(gf, text="N", command=lambda: self.gm.handle_input("go north"), **cfg).grid(row=0,column=1)
        tk.Button(gf, text="W", command=lambda: self.gm.handle_input("go west"), **cfg).grid(row=1,column=0)
        tk.Button(gf, text="E", command=lambda: self.gm.handle_input("go east"), **cfg).grid(row=1,column=2)
        tk.Button(gf, text="S", command=lambda: self.gm.handle_input("go south"), **cfg).grid(row=2,column=1)
        tk.Button(self.control_panel, text="🔍 搜刮 (Space)", bg="#d4af37", fg="black", font=("Arial",10,"bold"), command=lambda: self.gm.handle_input("search")).pack(fill="x", pady=4)
        tk.Button(self.control_panel, text="🎒 物品栏", bg="#444", fg="white", command=self.open_inventory).pack(fill="x", pady=2)
        tk.Button(self.control_panel, text="💾 保存", bg="#222", fg="#888", command=self.gm.save_game).pack(fill="x", pady=2)
        tk.Button(self.control_panel, text="🏠 菜单", bg="#222", fg="#888", command=self.gm.return_to_menu).pack(fill="x", pady=2)
    def _setup_combat_ui(self):
        tk.Button(self.control_panel, text="⚔ 攻击", bg="#cc0000", fg="white", font=("Arial",12,"bold"), height=2, command=lambda: self.gm.handle_combat("attack")).pack(fill="x", pady=10)
        tk.Button(self.control_panel, text="🏃 逃跑", bg="#555", fg="white", height=2, command=lambda: self.gm.handle_combat("run")).pack(fill="x", pady=5)
    def _setup_dialogue_ui(self, options):
        for idx, text in enumerate(options):
            tk.Button(self.control_panel, text=f"{idx+1}. {text}", bg="#330033", fg="white", anchor="w", font=("Arial",10), padx=10, command=lambda i=idx: self.gm.handle_dialogue(i)).pack(fill="x", pady=3)
    def open_inventory(self):
        inv = tk.Toplevel(self.root); inv.geometry("300x400"); inv.configure(bg="#222"); inv.title("Inventory")
        for i in self.gm.player.inventory: tk.Button(inv, text=i, bg="#444", fg="white", command=lambda n=i: [self.gm.try_use_item(n), inv.destroy()]).pack(fill="x", pady=1)
    def open_shop_window(self, shop_name, items):
        shop_win = tk.Toplevel(self.root); shop_win.geometry("400x500"); shop_win.configure(bg="#222")
        tk.Label(shop_win, text=shop_name, bg="#222", fg="gold", font=("Arial",14)).pack(pady=10)
        for n,p in items.items(): tk.Button(shop_win, text=f"{n} - ${p}", bg="#333", fg="white", command=lambda name=n,pr=p: self.gm.buy_item(name,pr)).pack(fill="x", padx=20, pady=2)
        tk.Button(shop_win, text="🎰 赌博 ($10)", bg="#400", fg="white", command=lambda: self.gm.gamble(10)).pack(fill="x", padx=20, pady=10)
    def show_death_screen(self):
        self._clear_frame(); self.current_frame = tk.Frame(self.root, bg="#1a0000"); self.current_frame.pack(fill="both", expand=True)
        tk.Label(self.current_frame, text="YOU DIED", font=("Times", 60), bg="#1a0000", fg="red").pack(pady=(200, 20))
        btn = {"font": ("Arial", 12), "width": 15, "bg": "#330000", "fg": "white"}
        tk.Button(self.current_frame, text="重新开始", command=self.gm.start_new_game, **btn).pack(pady=10)
        if self.gm.data_mgr.has_save_file(): tk.Button(self.current_frame, text="读档", command=self.gm.load_game, **btn).pack(pady=10)
        tk.Button(self.current_frame, text="主菜单", command=self.show_main_menu, **btn).pack(pady=10)
    def _setup_tags(self):
        self.text_area.tag_config("normal", foreground="#ccc"); self.text_area.tag_config("green", foreground="#33ff33")
        self.text_area.tag_config("red", foreground="#ff3333"); self.text_area.tag_config("yellow", foreground="#ffcc00")
        self.text_area.tag_config("cyan", foreground="#00ffff"); self.text_area.tag_config("gold", foreground="#ffd700"); self.text_area.tag_config("gray", foreground="#666")
    def append_text(self, t, tag="normal"): self.text_area.config(state="normal"); self.text_area.insert(tk.END, t+"\n", tag); self.text_area.see(tk.END); self.text_area.config(state="disabled")
    def update_main_text(self, t): self.append_text(t)
    def screen_flash(self, c, d=100):
        try: bg=self.text_area.cget("bg"); self.text_area.config(bg=c); self.root.after(d, lambda: self.text_area.config(bg=bg))
        except: pass
    def on_submit(self): c=self.entry.get(); self.entry.delete(0,tk.END); self.gm.handle_input(c)
    def start(self): self.root.mainloop()