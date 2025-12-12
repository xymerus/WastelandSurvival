# 文件路径: WastelandSurvival/src/models/quest.py
class Quest:
    def __init__(self, id, title, description, target_type, target_count, reward_xp, reward_caps):
        self.id = id
        self.title = title
        self.description = description
        self.target_type = target_type # 类型: "kill_zombie", "collect_water" 等
        self.target_count = target_count
        self.current_count = 0
        self.reward_xp = reward_xp
        self.reward_caps = reward_caps
        self.is_completed = False
        self.is_accepted = False

    def update_progress(self, amount=1):
        if self.is_completed or not self.is_accepted: return False
        self.current_count += amount
        if self.current_count >= self.target_count:
            self.current_count = self.target_count
            self.is_completed = True
            return True # 返回 True 表示任务刚完成
        return False

    def get_status_str(self):
        status = "[已完成]" if self.is_completed else f"({self.current_count}/{self.target_count})"
        return f"{self.title}\n  目标: {self.description} {status}\n"