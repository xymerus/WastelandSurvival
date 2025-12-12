# 文件路径: WastelandSurvival/main.py
import sys
import os

# --- 核心修复代码：将当前目录加入 Python 搜索路径 ---
# 这句代码告诉 Python：“在 main.py 所在的文件夹里找 src”
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# ------------------------------------------------

from src.systems.game_manager import GameManager

if __name__ == "__main__":
    game = GameManager()
    game.start()