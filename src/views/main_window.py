# 文件路径: WastelandSurvival/src/views/main_window.py
import tkinter as tk
from tkinter import ttk
import time

class MainWindow:
    def __init__(self, game_manager):
        self.gm = game_manager
        self.root = tk.Tk()
        self.root.title(">>> 废土行者 v2.1 (黑市版) <<<")
        self.root.geometry("1024x768")
        
        # 配色方案
        self.colors = {
            "bg": "#050505", "panel": "#101010", "text": "#cccccc",
            "highlight": "#33ff33", "danger": "#ff3333", "item": "#00ffff", 
            "story": "#ffcc00", "map_bg": "#001100", "gold": "#ffd700"
        }
        self.root.configure(bg=self.colors["bg"])
        
        # 样式配置
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("red.Horizontal.TProgressbar", foreground='red', background='#d10000', troughcolor='#220000', borderwidth=0)
        self.style.configure("green.Horizontal.TProgressbar", foreground='green', background='#00d100', troughcolor='#002200', borderwidth=0)

        self.current_frame = None
        self.control_panel = None 
        
        # [修复点]：初始化时不建立游戏界面，而是绑定全局键并显示主菜单
        self._bind_global_keys()
        self.show_main_menu()

    def _bind_global_keys(self):
        self.root.bind("<Return>", lambda e: self._on_enter())

    def _on_enter(self):
        # 只有在游戏界面且输入框存在时才响应回车
        if hasattr(self, 'entry') and self.entry.winfo_exists():
            cmd = self.entry.get()
            self.entry.delete(0, tk.END)
            self.gm.handle_input(cmd)

    # === 1. 主菜单 ===
    def show_main_menu(self):
        self._clear_frame()
        self.current_frame = tk.Frame(self.root, bg=self.colors["bg"])
        self.current_frame.pack(fill="both", expand=True)

        tk.Label(self.current_frame, text="WASTELAND WALKER", font=("Impact", 48), bg=self.colors["bg"], fg=self.colors["highlight"]).pack(pady=(150, 20))
        
        btn_style = {"font": ("Arial", 14, "bold"), "width": 20, "bg": "#222", "fg": "white", "bd": 1, "relief": "flat"}
        
        tk.Button(self.current_frame, text="新 游 戏", command=self.gm.start_new_game, **btn_style).pack(pady=10)
        
        state = "normal" if self.gm.data_mgr.has_save_file() else "disabled"
        # 避免参数冲突的写法
        load_btn_style = btn_style.copy()
        load_btn_style["fg"] = "white" if state == "normal" else "#444"
        tk.Button(self.current_frame, text="继续游戏", command=self.gm.load_game, state=state, **load_btn_style).pack(pady=10)
        
        tk.Button(self.current_frame, text="退 出", command=self.root.quit, **btn_style).pack(pady=10)

    # === 2. 死亡界面 ===
    def show_death_screen(self):
        self._clear_frame()
        self.current_frame = tk.Frame(self.root, bg="#1a0000")
        self.current_frame.pack(fill="both", expand=True)

        tk.Label(self.current_frame, text="YOU DIED", font=("Times", 60), bg="#1a0000", fg="red").pack(pady=(200, 20))
        
        btn = {"font": ("Arial", 12), "width": 15, "bg": "#330000", "fg": "white"}
        tk.Button(self.current_frame, text="重新开始", command=self.gm.start_new_game, **btn).pack(pady=10)
        
        if self.gm.data_mgr.has_save_file():
            tk.Button(self.current_frame, text="读档", command=self.gm.load_game, **btn).pack(pady=10)
            
        tk.Button(self.current_frame, text="主菜单", command=self.show_main_menu, **btn).pack(pady=10)

    # === 3. 游戏界面 ===
    def show_game_interface(self):
        self._clear_frame()
        self.current_frame = tk.Frame(self.root, bg=self.colors["bg"])
        self.current_frame.pack(fill="both", expand=True)
        
        self._bind_game_keys() # 重新绑定游戏键位

        main_pad = tk.Frame(self.current_frame, bg=self.colors["bg"])
        main_pad.pack(fill="both", expand=True, padx=20, pady=20)

        # 左面板
        left_panel = tk.Frame(main_pad, bg=self.colors["panel"])
        left_panel.pack(side="left", fill="both", expand=True)
        
        # HUD
        hud_frame = tk.Frame(left_panel, bg=self.colors["panel"], height=50)
        hud_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(hud_frame, text="HP", bg=self.colors["panel"], fg="red").pack(side="left")
        self.hp_bar = ttk.Progressbar(hud_frame, style="red.Horizontal.TProgressbar", length=100, maximum=100)
        self.hp_bar.pack(side="left", padx=5)
        
        tk.Label(hud_frame, text="饱食", bg=self.colors["panel"], fg="#00ff00").pack(side="left", padx=(10,0))
        self.hunger_bar = ttk.Progressbar(hud_frame, style="green.Horizontal.TProgressbar", length=100, maximum=100)
        self.hunger_bar.pack(side="left", padx=5)
        
        self.lvl_label = tk.Label(hud_frame, text="Lv.1", bg=self.colors["panel"], fg="white")
        self.lvl_label.pack(side="left", padx=10)
        self.caps_label = tk.Label(hud_frame, text="$ 50", bg=self.colors["panel"], fg=self.colors["gold"], font=("Arial", 10, "bold"))
        self.caps_label.pack(side="right", padx=10)

        # 文本区
        self.text_area = tk.Text(left_panel, bg="#080808", fg="#ccc", font=("Microsoft YaHei UI", 11), state="disabled", wrap="word", bd=0)
        self.text_area.pack(fill="both", expand=True)
        self._setup_tags()

        # 右面板
        right_panel = tk.Frame(main_pad, bg=self.colors["panel"], width=280)
        right_panel.pack(side="right", fill="y", padx=(15,0))
        right_panel.pack_propagate(False)
        
        tk.Label(right_panel, text="[ RADAR ]", bg="#222", fg="#666").pack(fill="x")
        self.map_area = tk.Text(right_panel, bg=self.colors["map_bg"], fg="#33ff33", font=("Courier New", 12, "bold"), height=9, width=22, state="disabled", bd=0)
        self.map_area.pack(pady=10)
        
        self.time_label = tk.Label(right_panel, text="--:--", bg=self.colors["panel"], fg="yellow", font=("Consolas", 16, "bold"))
        self.time_label.pack()
        
        self.control_panel = tk.Frame(right_panel, bg=self.colors["panel"])
        self.control_panel.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.entry = tk.Entry(right_panel, bg="#333", fg="white", relief="flat")
        self.entry.pack(side="bottom", fill="x", padx=10, pady=10)

    # === 4. 商店窗口 ===
    def open_shop_window(self, shop_name, items):
        shop_win = tk.Toplevel(self.root)
        shop_win.title(shop_name)
        shop_win.geometry("400x500")
        shop_win.configure(bg="#222")

        tk.Label(shop_win, text=shop_name, bg="#222", fg=self.colors["gold"], font=("Arial", 14)).pack(pady=10)
        
        for name, price in items.items():
            btn_text = f"{name}  -  ${price}"
            tk.Button(shop_win, text=btn_text, bg="#333", fg="white", 
                      command=lambda n=name, p=price: self.gm.buy_item(n, p)).pack(fill="x", padx=20, pady=2)

        tk.Label(shop_win, text="---", bg="#222", fg="#666").pack(pady=10)
        tk.Button(shop_win, text="🎰 赌博 ($10)", bg="#400", fg="white", 
                  command=lambda: self.gm.gamble(10)).pack(fill="x", padx=20, pady=5)

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
        if hasattr(self, 'hp_bar'): # 防止在菜单界面更新报错
            self.hp_bar['value'] = (player.hp / player.max_hp) * 100
            self.hunger_bar['value'] = player.hunger
            self.lvl_label.config(text=f"Lv.{player.level}")
            self.caps_label.config(text=f"$ {player.caps}")
            self.time_label.config(text=time_str)

    def switch_mode(self, mode, options=None):
        for w in self.control_panel.winfo_children(): w.destroy()
        if mode == "exploration": self._setup_exploration_ui()
        elif mode == "combat": self._setup_combat_ui()
        elif mode == "dialogue": self._setup_dialogue_ui(options)

    def _setup_exploration_ui(self):
        tk.Label(self.control_panel, text="WASD移动 | SPACE搜刮", bg="#101010", fg="#666").pack()
        gf = tk.Frame(self.control_panel, bg="#101010"); gf.pack(pady=10)
        cfg = {"width": 4, "bg": "#333", "fg": "white", "relief": "raised"}
        
        tk.Button(gf, text="N", command=lambda: self.gm.handle_input("go north"), **cfg).grid(row=0,column=1)
        tk.Button(gf, text="W", command=lambda: self.gm.handle_input("go west"), **cfg).grid(row=1,column=0,padx=5)
        tk.Button(gf, text="👁", command=lambda: self.gm.handle_input("look"), width=4, bg="#222", fg="#888").grid(row=1,column=1,pady=5)
        tk.Button(gf, text="E", command=lambda: self.gm.handle_input("go east"), **cfg).grid(row=1,column=2,padx=5)
        tk.Button(gf, text="S", command=lambda: self.gm.handle_input("go south"), **cfg).grid(row=2,column=1)
        
        tk.Button(self.control_panel, text="🔍 搜刮", bg="#d4af37", fg="black", command=lambda: self.gm.handle_input("search")).pack(fill="x", pady=2)
        tk.Button(self.control_panel, text="🎒 背包", bg="#4682b4", fg="white", command=self.open_inventory).pack(fill="x", pady=2)
        tk.Button(self.control_panel, text="💾 保存", bg="#444", fg="white", command=self.gm.save_game).pack(fill="x", pady=2)
        tk.Button(self.control_panel, text="🏠 菜单", bg="#222", fg="#888", command=self.gm.return_to_menu).pack(fill="x", pady=2)

    def _setup_combat_ui(self):
        tk.Label(self.control_panel, text="⚠ 战斗 ⚠", bg="red", fg="white").pack(fill="x", pady=20)
        tk.Button(self.control_panel, text="⚔ 攻击", bg="#cc0000", fg="white", height=3, command=lambda: self.gm.handle_combat("attack")).pack(fill="x", pady=10)
        tk.Button(self.control_panel, text="🏃 逃跑", bg="#555", fg="white", command=lambda: self.gm.handle_combat("run")).pack(fill="x", pady=5)

    def _setup_dialogue_ui(self, options):
        tk.Label(self.control_panel, text="🗨 剧情", bg="#550055", fg="white").pack(fill="x", pady=10)
        for idx, text in enumerate(options):
            tk.Button(self.control_panel, text=f"{idx+1}. {text}", bg="#330033", fg="white", height=2, anchor="w", padx=10, 
                      command=lambda i=idx: self.gm.handle_dialogue(i)).pack(fill="x", pady=2)

    def open_inventory(self):
        inv = tk.Toplevel(self.root); inv.geometry("300x400"); inv.configure(bg="#222")
        for i in self.gm.player.inventory: 
            tk.Button(inv, text=i, bg="#444", fg="white", command=lambda n=i: [self.gm.try_use_item(n), inv.destroy()]).pack(fill="x", pady=1)

    def _setup_tags(self):
        self.text_area.tag_config("normal", foreground="#cccccc"); self.text_area.tag_config("green", foreground="#33ff33")
        self.text_area.tag_config("red", foreground="#ff3333"); self.text_area.tag_config("yellow", foreground="#ffcc00")
        self.text_area.tag_config("cyan", foreground="#00ffff"); self.text_area.tag_config("gold", foreground="#ffd700")
        self.text_area.tag_config("gray", foreground="#666")

    def append_text(self, t, tag="normal"):
        self.text_area.config(state="normal")
        self.text_area.insert(tk.END, t+"\n", tag)
        self.text_area.see(tk.END)
        self.text_area.config(state="disabled")

    def update_main_text(self, t): self.append_text(t)
    
    def update_map(self, m):
        if hasattr(self, 'map_area'):
            self.map_area.config(state="normal")
            self.map_area.delete(1.0, tk.END)
            self.map_area.insert(tk.END, m)
            self.map_area.config(state="disabled")

    def screen_flash(self, c, d=100):
        try: bg=self.text_area.cget("bg"); self.text_area.config(bg=c); self.root.after(d, lambda: self.text_area.config(bg=bg))
        except: pass
    
    def on_submit(self): c=self.entry.get(); self.entry.delete(0,tk.END); self.gm.handle_input(c)
    def start(self): self.root.mainloop()