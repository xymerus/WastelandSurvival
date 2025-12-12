# 文件路径: WastelandSurvival/src/views/main_window.py
import tkinter as tk
from tkinter import ttk

class MainWindow:
    def __init__(self, game_manager):
        self.gm = game_manager
        self.root = tk.Tk()
        self.root.title(">>> 废土行者 v2.0 (RPG版) <<<")
        self.root.geometry("1024x768")
        self.colors = {"bg": "#050505", "panel": "#101010", "highlight": "#33ff33", "danger": "#ff3333", "story": "#ffcc00", "map": "#001100"}
        self.root.configure(bg=self.colors["bg"])
        
        # 样式配置
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("red.Horizontal.TProgressbar", foreground='red', background='#d10000', troughcolor='#220000', borderwidth=0)
        self.style.configure("green.Horizontal.TProgressbar", foreground='green', background='#00d100', troughcolor='#002200', borderwidth=0)
        
        # 容器管理
        self.current_frame = None
        self._bind_global_keys()
        
        # 启动时显示主菜单
        self.show_main_menu()

    def _bind_global_keys(self):
        self.root.bind("<Return>", lambda e: self._on_enter())

    def _on_enter(self):
        if hasattr(self, 'entry') and self.entry.winfo_exists():
            cmd = self.entry.get()
            self.entry.delete(0, tk.END)
            self.gm.handle_input(cmd)

    # === 1. 主菜单界面 (修复了报错) ===
    def show_main_menu(self):
        self._clear_frame()
        self.current_frame = tk.Frame(self.root, bg=self.colors["bg"])
        self.current_frame.pack(fill="both", expand=True)

        # 标题
        tk.Label(self.current_frame, text="WASTELAND WALKER", font=("Impact", 48), bg=self.colors["bg"], fg=self.colors["highlight"]).pack(pady=(150, 20))
        tk.Label(self.current_frame, text="v2.0 - RPG Survival", font=("Arial", 12), bg=self.colors["bg"], fg="#666").pack(pady=(0, 50))

        # 按钮通用样式
        btn_style = {"font": ("Arial", 14, "bold"), "width": 20, "bg": "#222", "fg": "white", "bd": 1, "relief": "flat"}
        
        # 新游戏按钮
        tk.Button(self.current_frame, text="新 游 戏 (New Game)", command=self.gm.start_new_game, **btn_style).pack(pady=10)
        
        # 继续游戏按钮 (修复点：先复制样式，再修改颜色，避免参数冲突)
        state = "normal" if self.gm.data_mgr.has_save_file() else "disabled"
        load_color = "white" if state == "normal" else "#444"
        
        load_style = btn_style.copy() # 复制一份字典
        load_style["fg"] = load_color # 修改其中的颜色
        
        tk.Button(self.current_frame, text="继续游戏 (Load Game)", command=self.gm.load_game, state=state, **load_style).pack(pady=10)
        
        # 退出按钮
        tk.Button(self.current_frame, text="退 出 (Quit)", command=self.root.quit, **btn_style).pack(pady=10)

    # === 2. 死亡界面 ===
    def show_death_screen(self):
        self._clear_frame()
        self.current_frame = tk.Frame(self.root, bg="#1a0000")
        self.current_frame.pack(fill="both", expand=True)

        tk.Label(self.current_frame, text="YOU DIED", font=("Times New Roman", 60, "bold"), bg="#1a0000", fg="red").pack(pady=(200, 20))
        tk.Label(self.current_frame, text="废土吞噬了你的尸骨...", font=("Arial", 14), bg="#1a0000", fg="#ff8888").pack(pady=(0, 50))

        btn_style = {"font": ("Arial", 12), "width": 15, "bg": "#330000", "fg": "white", "bd": 1}
        tk.Button(self.current_frame, text="重新开始", command=self.gm.start_new_game, **btn_style).pack(pady=10)
        
        if self.gm.data_mgr.has_save_file():
            tk.Button(self.current_frame, text="读取上一次存档", command=self.gm.load_game, **btn_style).pack(pady=10)
            
        tk.Button(self.current_frame, text="返回主菜单", command=self.show_main_menu, **btn_style).pack(pady=10)

    # === 3. 游戏主界面 ===
    def show_game_interface(self):
        self._clear_frame()
        self.current_frame = tk.Frame(self.root, bg=self.colors["bg"])
        self.current_frame.pack(fill="both", expand=True)
        
        self._bind_game_keys()

        main_pad = tk.Frame(self.current_frame, bg=self.colors["bg"])
        main_pad.pack(fill="both", expand=True, padx=20, pady=20)

        # 左侧面板
        left_panel = tk.Frame(main_pad, bg=self.colors["panel"]); left_panel.pack(side="left", fill="both", expand=True)
        
        # HUD
        hud_frame = tk.Frame(left_panel, bg=self.colors["panel"], height=50); hud_frame.pack(fill="x", padx=10, pady=10)
        tk.Label(hud_frame, text="HP", bg=self.colors["panel"], fg="red").pack(side="left")
        self.hp_bar = ttk.Progressbar(hud_frame, style="red.Horizontal.TProgressbar", length=120, maximum=100); self.hp_bar.pack(side="left", padx=5)
        
        tk.Label(hud_frame, text="XP", bg=self.colors["panel"], fg="#aaaaff").pack(side="left", padx=(10,0))
        self.xp_bar = ttk.Progressbar(hud_frame, length=100); self.xp_bar.pack(side="left", padx=5)
        self.lvl_label = tk.Label(hud_frame, text="Lv.1", bg=self.colors["panel"], fg="white"); self.lvl_label.pack(side="left")

        # 文本区
        self.text_area = tk.Text(left_panel, bg="#080808", fg="#ccc", font=("Microsoft YaHei UI", 11), state="disabled", wrap="word", bd=0)
        self.text_area.pack(fill="both", expand=True)
        self._setup_tags()

        # 右侧面板
        right_panel = tk.Frame(main_pad, bg=self.colors["panel"], width=280); right_panel.pack(side="right", fill="y", padx=(15,0)); right_panel.pack_propagate(False)
        
        # 地图 & 时间
        tk.Label(right_panel, text="[ RADAR ]", bg="#222", fg="#666").pack(fill="x")
        self.map_area = tk.Text(right_panel, bg=self.colors["map"], fg="#33ff33", font=("Courier New", 12, "bold"), height=9, width=22, state="disabled", bd=0); self.map_area.pack(pady=10)
        self.time_label = tk.Label(right_panel, text="--:--", bg=self.colors["panel"], fg="yellow", font=("Consolas", 16, "bold")); self.time_label.pack()

        # 控制区
        self.control_panel = tk.Frame(right_panel, bg=self.colors["panel"]); self.control_panel.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 输入框
        self.entry = tk.Entry(right_panel, bg="#333", fg="white", relief="flat"); self.entry.pack(side="bottom", fill="x", padx=10, pady=10)

    # === 辅助方法 ===
    def _clear_frame(self):
        if self.current_frame: self.current_frame.destroy()
    
    def _bind_game_keys(self):
        self.root.bind("<w>", lambda e: self.gm.handle_input("go north"))
        self.root.bind("<s>", lambda e: self.gm.handle_input("go south"))
        self.root.bind("<a>", lambda e: self.gm.handle_input("go west"))
        self.root.bind("<d>", lambda e: self.gm.handle_input("go east"))
        self.root.bind("<space>", lambda e: self.gm.handle_input("search"))

    def update_stats(self, player, time_str):
        self.hp_bar['value'] = (player.hp / player.max_hp) * 100
        self.xp_bar['value'] = (player.xp / player.xp_to_next_level) * 100
        self.lvl_label.config(text=f"Lv.{player.level}")
        self.time_label.config(text=time_str)

    def switch_mode(self, mode, options=None):
        for w in self.control_panel.winfo_children(): w.destroy()
        if mode == "exploration": self._setup_exploration_ui()
        elif mode == "combat": self._setup_combat_ui()
        elif mode == "dialogue": self._setup_dialogue_ui(options)

    def _setup_exploration_ui(self):
        tk.Label(self.control_panel, text="WASD移动 | SPACE搜刮", bg="#101010", fg="#666").pack()
        grid_frame = tk.Frame(self.control_panel, bg="#101010"); grid_frame.pack(pady=10)
        btn_opts = {"width": 4, "bg": "#333", "fg": "white", "relief": "raised"}
        
        tk.Button(grid_frame, text="N", command=lambda: self.gm.handle_input("go north"), **btn_opts).grid(row=0, column=1)
        tk.Button(grid_frame, text="W", command=lambda: self.gm.handle_input("go west"), **btn_opts).grid(row=1, column=0, padx=5)
        tk.Button(grid_frame, text="👁", command=lambda: self.gm.handle_input("look"), width=4, bg="#222", fg="#888").grid(row=1, column=1, pady=5)
        tk.Button(grid_frame, text="E", command=lambda: self.gm.handle_input("go east"), **btn_opts).grid(row=1, column=2, padx=5)
        tk.Button(grid_frame, text="S", command=lambda: self.gm.handle_input("go south"), **btn_opts).grid(row=2, column=1)
        
        tk.Button(self.control_panel, text="🔍 搜刮", bg="#d4af37", fg="black", command=lambda: self.gm.handle_input("search")).pack(fill="x", pady=2)
        tk.Button(self.control_panel, text="🎒 背包", bg="#4682b4", fg="white", command=self.open_inventory).pack(fill="x", pady=2)
        tk.Button(self.control_panel, text="💾 保存进度", bg="#444", fg="white", command=self.gm.save_game).pack(fill="x", pady=2)
        tk.Button(self.control_panel, text="🏠 主菜单", bg="#222", fg="#888", command=self.gm.return_to_menu).pack(fill="x", pady=2)

    def _setup_combat_ui(self):
        tk.Label(self.control_panel, text="⚠ 战斗状态 ⚠", bg="red", fg="white", font=("Arial", 12, "bold")).pack(fill="x", pady=20)
        tk.Button(self.control_panel, text="⚔ 全力攻击", bg="#cc0000", fg="white", font=("Arial", 12, "bold"), height=3, command=lambda: self.gm.handle_combat("attack")).pack(fill="x", pady=10)
        tk.Button(self.control_panel, text="🏃 尝试逃跑", bg="#555", fg="white", height=2, command=lambda: self.gm.handle_combat("run")).pack(fill="x", pady=5)

    def _setup_dialogue_ui(self, options):
        tk.Label(self.control_panel, text="🗨 剧情互动", bg="#550055", fg="white").pack(fill="x", pady=10)
        for idx, text in enumerate(options):
            tk.Button(self.control_panel, text=f"{idx+1}. {text}", bg="#330033", fg="white", height=2, anchor="w", padx=10,
                      command=lambda i=idx: self.gm.handle_dialogue(i)).pack(fill="x", pady=2)

    def open_inventory(self):
        inv = tk.Toplevel(self.root); inv.geometry("300x400"); inv.title("Inventory"); inv.configure(bg="#222")
        if not self.gm.player.inventory: tk.Label(inv, text="背包是空的", bg="#222", fg="#888").pack(pady=20)
        for i in self.gm.player.inventory: 
            tk.Button(inv, text=i, bg="#444", fg="white", command=lambda n=i: [self.gm.try_use_item(n), inv.destroy()]).pack(fill="x", pady=1)

    def _setup_tags(self):
        self.text_area.tag_config("normal", foreground="#cccccc"); self.text_area.tag_config("green", foreground="#33ff33"); self.text_area.tag_config("red", foreground="#ff3333")
        self.text_area.tag_config("yellow", foreground="#ffcc00"); self.text_area.tag_config("cyan", foreground="#00ffff"); self.text_area.tag_config("gray", foreground="#666")

    def append_text(self, t, tag="normal"):
        self.text_area.config(state="normal"); self.text_area.insert(tk.END, t+"\n", tag); self.text_area.see(tk.END); self.text_area.config(state="disabled")
    
    def update_main_text(self, t): self.append_text(t)
    
    def update_map(self, m):
        self.map_area.config(state="normal"); self.map_area.delete(1.0,tk.END); self.map_area.insert(tk.END,m); self.map_area.config(state="disabled")
    
    def screen_flash(self, c, d=100):
        try:
            bg=self.text_area.cget("bg"); self.text_area.config(bg=c); self.root.after(d, lambda: self.text_area.config(bg=bg))
        except: pass

    def on_submit(self): c=self.entry.get(); self.entry.delete(0,tk.END); self.gm.handle_input(c)
    def start(self): self.root.mainloop()