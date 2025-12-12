# 文件路径: WastelandSurvival/src/utils/data_manager.py
import json
import os

SAVE_FILE = "savegame.json"

class DataManager:
    @staticmethod
    def save_game(player, current_location_name, time_hour):
        data = {
            "player": {
                "name": player.name,
                "hp": player.hp,
                "max_hp": player.max_hp,
                "hunger": player.hunger,
                "inventory": player.inventory,
                "companions": player.companions,
                "xp": player.xp,
                "level": player.level,
                "caps": player.caps # [新增] 保存瓶盖
            },
            "game": {
                "location": current_location_name,
                "time": time_hour
            }
        }
        try:
            with open(SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Save failed: {e}")
            return False

    @staticmethod
    def load_game():
        if not os.path.exists(SAVE_FILE):
            return None
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Load failed: {e}")
            return None
            
    @staticmethod
    def has_save_file():
        return os.path.exists(SAVE_FILE)