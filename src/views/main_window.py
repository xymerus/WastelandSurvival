# 文件路径: WastelandSurvival/src/views/main_window.py
import tkinter as tk
from tkinter import ttk
import time

class MainWindow:
    def __init__(self, game_manager):
        self.gm = game_manager
        self.root = tk.Tk()
        self.root.title(">>> 废土行者 v2.2 (英雄之路) <<<")
        self.root.geometry("1100x768") # 稍微宽一点
        
        self.colors = {
            "bg": "#050505", "panel": "#101010", "text": "#cccccc",
            "highlight": "#33ff33", "danger": "#ff3333", "item": "#00ffff", 
            "story": "#ffcc00", "map_bg": "#001100", "gold": "#ffd700",
            "tab_bg": "#202020"
        }
        self.root.configure(bg=self.colors["bg"])
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("red.Horizontal.TProgressbar", foreground='red', background='#d10000', troughcolor='#220000', borderwidth=0)
        self.style.configure("green.Horizontal.TProgressbar", foreground='green', background='#00d100', troughcolor='#002200', borderwidth=0)
        # Tab 样式
        self.style.configure("TNotebook", background=self.colors["bg"], borderwidth=0)
        self.style.configure("TNotebook.Tab", background="#333", foreground="white", padding=[10, 5])
        self.style.map("TNotebook.Tab", background=[("selected", "#555")], foreground=[("selected", self.colors["highlight"])])

        self.current_frame = None
        self._bind_global_keys()
        self.show_main_menu()

    # (保留 _bind_global_keys, _on_enter, show_main_menu, show_death_screen)
    def _bind_global_keys(self): self.root.bind("<Return>", lambda e: self._on_enter())
    def _on_enter(self): 
        if hasattr(self, 'entry') and self.entry.winfo_exists():
            c=self.entry.get(); self.entry.delete(0,tk.END); self.gm.handle_input(c)

    def show_main_menu(self):
        self._clear_frame(); self.current_frame = tk.Frame(self.root, bg=self.colors["bg"]); self.current_frame.pack(fill="both", expand=True)
        tk.Label(self.current_frame, text="WASTELAND WALKER", font=("Impact", 48), bg=self.colors["bg"], fg=self.colors["highlight"]).pack(pady=(150, 20))
        btn = {"font": ("Arial", 14), "width": 20, "bg": "#222", "fg": "white", "bd": 1, "relief": "flat"}
        tk.Button(self.current_frame, text="新 游 戏", command=self.gm.start_new_game, **btn).pack(pady=10)
        s = "normal" if self.gm.data_mgr.has_save_file() else "disabled"
        l_btn = btn.copy(); l_btn["fg"] = "white" if s=="normal" else "#444"
        tk.Button(self.current_frame, text="继续游戏", command=self.gm.load_game, state=s, **l_btn).pack(pady=10)
        tk.Button(self.current_frame, text="退 出", command=self.root.quit, **btn).pack(pady=10)

    def show_death_screen(self):
        self._clear_frame(); self.current_frame = tk.Frame(self.root, bg="#1a0000"); self.current_frame.pack(fill="both", expand=True)
        tk.Label(self.current_frame, text="YOU DIED", font=("Times", 60), bg="#1a0000", fg="red").pack(pady=(200, 20))
        btn = {"font": ("Arial", 12), "width": 15, "bg": "#330000", "fg": "white"}
        tk.Button(self.current_frame, text="重新开始", command=self.gm.start_new_game, **btn).pack(pady=10)
        if self.gm.data_mgr.has_save_file(): tk.Button(self.current_frame, text="读档", command=self.gm.load_game, **btn).pack(pady=10)
        tk.Button(self.current_frame, text="主菜单", command=self.show_main_menu, **btn).pack(pady=10)

    # === [修改] 游戏界面：右侧改为 Notebook ===
    def show_game_interface(self):
        self._clear_frame()
        self.current_frame = tk.Frame(self.root, bg=self.colors["bg"])
        self.current_frame.pack(fill="both", expand=True)
        self._bind_game_keys()

        main_pad = tk.Frame(self.current_frame, bg=self.colors["bg"])
        main_pad.pack(fill="both", expand=True, padx=20, pady=20)

        # 左侧面板 (HUD + 文本)
        left_panel = tk.Frame(main_pad, bg=self.colors["panel"])
        left_panel.pack(side="left", fill="both", expand=True)
        
        hud_frame = tk.Frame(left_panel, bg=self.colors["panel"], height=50)
        hud_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(hud_frame, text="HP", bg=self.colors["panel"], fg="red").pack(side="left")
        self.hp_bar = ttk.Progressbar(hud_frame, style="red.Horizontal.TProgressbar", length=100, maximum=100); self.hp_bar.pack(side="left", padx=5)
        tk.Label(hud_frame, text="饱食", bg=self.colors["panel"], fg="#00ff00").pack(side="left", padx=(10,0))
        self.hunger_bar = ttk.Progressbar(hud_frame, style="green.Horizontal.TProgressbar", length=100, maximum=100); self.hunger_bar.pack(side="left", padx=5)
        self.lvl_label = tk.Label(hud_frame, text="Lv.1", bg=self.colors["panel"], fg="white"); self.lvl_label.pack(side="left", padx=10)
        self.caps_label = tk.Label(hud_frame, text="$ 50", bg=self.colors["panel"], fg=self.colors["gold"], font=("Arial", 10, "bold")); self.caps_label.pack(side="right", padx=10)

        self.text_area = tk.Text(left_panel, bg="#080808", fg="#ccc", font=("Microsoft YaHei UI", 11), state="disabled", wrap="word", bd=0)
        self.text_area.pack(fill="both", expand=True)
        self._setup_tags()

        # === [核心修改] 右侧面板：Notebook ===
        right_panel = tk.Frame(main_pad, bg=self.colors["panel"], width=320) # 稍微加宽
        right_panel.pack(side="right", fill="y", padx=(15,0))
        right_panel.pack_propagate(False)

        # 创建选项卡
        self.tabs = ttk.Notebook(right_panel)
        self.tabs.pack(fill="both", expand=True)

        # Tab 1: 控制台 (地图 + 按钮)
        self.tab_console = tk.Frame(self.tabs, bg=self.colors["panel"])
        self.tabs.add(self.tab_console, text="控制")
        self._init_console_tab()

        # Tab 2: 任务日志
        self.tab_quest = tk.Frame(self.tabs, bg=self.colors["panel"])
        self.tabs.add(self.tab_quest, text="任务")
        self.quest_text = tk.Text(self.tab_quest, bg="#111", fg="#aaa", font=("Consolas", 10), state="disabled", bd=0, padx=10, pady=10)
        self.quest_text.pack(fill="both", expand=True)

        # 底部输入框 (全局)
        self.entry = tk.Entry(right_panel, bg="#333", fg="white", relief="flat")
        self.entry.pack(side="bottom", fill="x", padx=5, pady=5)

    def _init_console_tab(self):
        # 地图区
        tk.Label(self.tab_console, text="[ RADAR ]", bg=self.colors["panel"], fg="#666").pack(fill="x", pady=(10,0))
        self.map_area = tk.Text(self.tab_console, bg=self.colors["map_bg"], fg="#33ff33", font=("Courier New", 12, "bold"), height=9, width=22, state="disabled", bd=0)
        self.map_area.pack(pady=5)
        self.time_label = tk.Label(self.tab_console, text="--:--", bg=self.colors["panel"], fg="yellow", font=("Consolas", 16, "bold"))
        self.time_label.pack()
        
        # 按钮容器
        self.control_panel = tk.Frame(self.tab_console, bg=self.colors["panel"])
        self.control_panel.pack(fill="both", expand=True, padx=5, pady=5)

    # === [新增] 更新任务列表显示 ===
    def update_quest_log(self, quests):
        if not hasattr(self, 'quest_text'): return
        self.quest_text.config(state="normal")
        self.quest_text.delete(1.0, tk.END)
        
        if not quests:
            self.quest_text.insert(tk.END, "当前没有活跃任务。\n请寻找 NPC 接取任务。")
        else:
            for q in quests:
                color = "green" if q.is_completed else "white"
                self.quest_text.insert(tk.END, q.get_status_str() + "\n")
        
        self.quest_text.config(state="disabled")

    # (保留原有 UI 更新方法)
    def update_stats(self, player, time_str):
        if hasattr(self, 'hp_bar'):
            self.hp_bar['value'] = (player.hp / player.max_hp) * 100
            self.hunger_bar['value'] = player.hunger
            self.lvl_label.config(text=f"Lv.{player.level}")
            self.caps_label.config(text=f"$ {player.caps}")
            self.time_label.config(text=time_str)
            # 顺便更新任务
            self.update_quest_log(player.active_quests)

    # (保留其他方法: _clear_frame, _bind_game_keys, switch_mode, open_inventory, open_shop_window, _setup_tags, append_text...)
    # 务必保留 v2.1 的这些实现，这里简写
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
        # 简化版布局，适应新宽度
        gf = tk.Frame(self.control_panel, bg="#101010"); gf.pack(pady=5)
        cfg = {"width": 3, "bg": "#333", "fg": "white"}
        tk.Button(gf, text="N", command=lambda: self.gm.handle_input("go north"), **cfg).grid(row=0,column=1)
        tk.Button(gf, text="W", command=lambda: self.gm.handle_input("go west"), **cfg).grid(row=1,column=0)
        tk.Button(gf, text="E", command=lambda: self.gm.handle_input("go east"), **cfg).grid(row=1,column=2)
        tk.Button(gf, text="S", command=lambda: self.gm.handle_input("go south"), **cfg).grid(row=2,column=1)
        
        tk.Button(self.control_panel, text="🔍 搜刮", bg="#d4af37", fg="black", command=lambda: self.gm.handle_input("search")).pack(fill="x", pady=2)
        tk.Button(self.control_panel, text="🎒 背包", bg="#4682b4", fg="white", command=self.open_inventory).pack(fill="x", pady=2)
        tk.Button(self.control_panel, text="💾 保存", bg="#444", fg="white", command=self.gm.save_game).pack(fill="x", pady=2)
        tk.Button(self.control_panel, text="🏠 菜单", bg="#222", fg="#888", command=self.gm.return_to_menu).pack(fill="x", pady=2)

    def _setup_combat_ui(self):
        tk.Button(self.control_panel, text="⚔ 攻击", bg="#cc0000", fg="white", height=3, command=lambda: self.gm.handle_combat("attack")).pack(fill="x", pady=10)
        tk.Button(self.control_panel, text="🏃 逃跑", bg="#555", fg="white", command=lambda: self.gm.handle_combat("run")).pack(fill="x", pady=5)
    
    def _setup_dialogue_ui(self, options):
        for idx, text in enumerate(options):
            tk.Button(self.control_panel, text=f"{idx+1}. {text}", bg="#330033", fg="white", anchor="w", command=lambda i=idx: self.gm.handle_dialogue(i)).pack(fill="x", pady=2)

    def open_inventory(self):
        inv = tk.Toplevel(self.root); inv.geometry("300x400"); inv.configure(bg="#222")
        for i in self.gm.player.inventory: tk.Button(inv, text=i, bg="#444", fg="white", command=lambda n=i: [self.gm.try_use_item(n), inv.destroy()]).pack(fill="x", pady=1)
    
    def open_shop_window(self, shop_name, items):
        # 复制 v2.1 的商店代码
        shop_win = tk.Toplevel(self.root); shop_win.geometry("400x500"); shop_win.configure(bg="#222")
        tk.Label(shop_win, text=shop_name, bg="#222", fg="gold", font=("Arial",14)).pack(pady=10)
        for n,p in items.items(): tk.Button(shop_win, text=f"{n} - ${p}", bg="#333", fg="white", command=lambda name=n,pr=p: self.gm.buy_item(name,pr)).pack(fill="x", padx=20, pady=2)
        tk.Button(shop_win, text="🎰 赌博 ($10)", bg="#400", fg="white", command=lambda: self.gm.gamble(10)).pack(fill="x", padx=20, pady=10)

    def _setup_tags(self):
        self.text_area.tag_config("normal", foreground="#ccc"); self.text_area.tag_config("green", foreground="#33ff33")
        self.text_area.tag_config("red", foreground="#ff3333"); self.text_area.tag_config("yellow", foreground="#ffcc00")
        self.text_area.tag_config("cyan", foreground="#00ffff"); self.text_area.tag_config("gold", foreground="#ffd700"); self.text_area.tag_config("gray", foreground="#666")
    def append_text(self, t, tag="normal"): self.text_area.config(state="normal"); self.text_area.insert(tk.END, t+"\n", tag); self.text_area.see(tk.END); self.text_area.config(state="disabled")
    def update_main_text(self, t): self.append_text(t)
    def update_map(self, m): 
        if hasattr(self, 'map_area'): self.map_area.config(state="normal"); self.map_area.delete(1.0,tk.END); self.map_area.insert(tk.END,m); self.map_area.config(state="disabled")
    def screen_flash(self, c, d=100):
        try: bg=self.text_area.cget("bg"); self.text_area.config(bg=c); self.root.after(d, lambda: self.text_area.config(bg=bg))
        except: pass
    def on_submit(self): c=self.entry.get(); self.entry.delete(0,tk.END); self.gm.handle_input(c)
    def start(self): self.root.mainloop()