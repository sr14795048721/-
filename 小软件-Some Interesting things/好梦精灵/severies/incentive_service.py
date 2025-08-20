import json
import os
from datetime import datetime

class IncentiveService:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.points_file = os.path.join(data_dir, 'user_points.json')
        self.badges_file = os.path.join(data_dir, 'user_badges.json')
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def add_points(self, user_id, points, reason=""):
        """
        为用户添加积分
        :param user_id: 用户ID
        :param points: 积分数量
        :param reason: 积分原因
        """
        user_points = self._load_user_points()
        
        if user_id not in user_points:
            user_points[user_id] = 0
            
        user_points[user_id] += points
        
        # 记录积分变动历史
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'points': points,
            'reason': reason
        }
        
        self._save_user_points(user_points)
        self._record_points_history(user_id, history_entry)
        
        return user_points[user_id]
    
    def get_user_points(self, user_id):
        """
        获取用户积分
        :param user_id: 用户ID
        :return: 用户积分
        """
        user_points = self._load_user_points()
        return user_points.get(user_id, 0)
    
    def award_badge(self, user_id, badge_name):
        """
        授予用户徽章
        :param user_id: 用户ID
        :param badge_name: 徽章名称
        """
        user_badges = self._load_user_badges()
        
        if user_id not in user_badges:
            user_badges[user_id] = []
            
        if badge_name not in user_badges[user_id]:
            user_badges[user_id].append(badge_name)
            self._save_user_badges(user_badges)
            return True
        return False
    
    def get_user_badges(self, user_id):
        """
        获取用户徽章
        :param user_id: 用户ID
        :return: 用户徽章列表
        """
        user_badges = self._load_user_badges()
        return user_badges.get(user_id, [])
    
    def check_achievements(self, user_id, action, data):
        """
        检查用户是否达成成就
        :param user_id: 用户ID
        :param action: 行为类型
        :param data: 行为数据
        """
        badges_awarded = []
        
        # 根据行为检查成就
        if action == "analyze_sleep":
            # 连续分析成就
            if self._check_consecutive_days(user_id, "analyze_sleep") >= 7:
                if self.award_badge(user_id, "weekly_analyzer"):
                    badges_awarded.append("weekly_analyzer")
                    
        elif action == "analyze_behavior":
            # 健康评分成就
            if data.get('score', 0) >= 90:
                if self.award_badge(user_id, "health_master"):
                    badges_awarded.append("health_master")
        
        return badges_awarded
    
    def _check_consecutive_days(self, user_id, action):
        """
        检查连续天数
        :param user_id: 用户ID
        :param action: 行为类型
        :return: 连续天数
        """
        # 简化实现，实际应用中需要检查历史记录
        return 1
    
    def _load_user_points(self):
        """加载用户积分数据"""
        if os.path.exists(self.points_file):
            with open(self.points_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_user_points(self, user_points):
        """保存用户积分数据"""
        with open(self.points_file, 'w', encoding='utf-8') as f:
            json.dump(user_points, f, ensure_ascii=False, indent=2)
    
    def _load_user_badges(self):
        """加载用户徽章数据"""
        if os.path.exists(self.badges_file):
            with open(self.badges_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_user_badges(self, user_badges):
        """保存用户徽章数据"""
        with open(self.badges_file, 'w', encoding='utf-8') as f:
            json.dump(user_badges, f, ensure_ascii=False, indent=2)
    
    def _record_points_history(self, user_id, entry):
        """记录积分历史"""
        history_file = os.path.join(self.data_dir, f'points_history_{user_id}.json')
        history = []
        
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        history.append(entry)
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)