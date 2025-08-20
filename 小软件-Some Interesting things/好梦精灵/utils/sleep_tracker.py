import datetime
import json
import os
from .system_info import SystemInfo

class SleepTracker:
    def __init__(self):
        self.data_file = 'sleep_data.json'
        self.sleep_data = self.load_data()
    
    def load_data(self):
        """加载睡眠数据"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_data(self):
        """保存睡眠数据"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.sleep_data, f, ensure_ascii=False, indent=2)
    
    def detect_sleep_pattern(self):
        """检测睡眠模式"""
        sys_info = SystemInfo.get_system_info()
        current_hour = datetime.datetime.now().hour
        
        # 检测是否为睡眠时间（22:00-06:00）
        is_sleep_time = current_hour >= 22 or current_hour <= 6
        
        # 检测屏幕活动
        screen_active = sys_info['screen_time_hours'] > 0.1  # 最近有屏幕活动
        
        return {
            'is_sleep_time': is_sleep_time,
            'screen_active': screen_active,
            'current_hour': current_hour,
            'estimated_sleep_start': self.estimate_sleep_start(),
            'estimated_sleep_duration': self.estimate_sleep_duration()
        }
    
    def estimate_sleep_start(self):
        """估算入睡时间"""
        current_time = datetime.datetime.now()
        
        # 如果是凌晨，假设昨晚22:30入睡
        if current_time.hour <= 6:
            sleep_start = current_time.replace(hour=22, minute=30, second=0) - datetime.timedelta(days=1)
        else:
            # 如果是白天，返回None
            return None
            
        return sleep_start.strftime('%H:%M')
    
    def estimate_sleep_duration(self):
        """估算睡眠时长"""
        current_time = datetime.datetime.now()
        
        # 如果是早晨6-10点，计算从昨晚22:30到现在的时长
        if 6 <= current_time.hour <= 10:
            sleep_start = current_time.replace(hour=22, minute=30, second=0) - datetime.timedelta(days=1)
            duration = (current_time - sleep_start).total_seconds() / 3600
            return round(duration, 1)
        
        return None
    
    def analyze_sleep_quality(self, sleep_hours, bedtime):
        """分析睡眠质量 - 优化版"""
        from utils.health_calculator import HealthCalculator
        
        quality_score = HealthCalculator.calculate_sleep_score(sleep_hours, bedtime)
        health_level = HealthCalculator.get_health_level(quality_score)
        
        suggestions = []
        if quality_score < 5:
            suggestions.append("睡眠质量较差，建议调整作息时间和睡眠环境")
        elif quality_score < 7:
            suggestions.append("睡眠质量一般，建议21:00-23:30入睡，保证7-9小时睡眠")
        else:
            suggestions.append("睡眠质量良好，请继续保持")
        
        # 记录睡眠数据
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        self.sleep_data[today] = {
            'sleep_hours': sleep_hours,
            'bedtime': bedtime,
            'quality_score': quality_score
        }
        self.save_data()
        
        return {
            'quality_score': quality_score,
            'suggestions': suggestions,
            'sleep_efficiency': health_level['level'],
            'health_level': health_level
        }
    
    def calculate_efficiency(self, sleep_hours):
        """计算睡眠效率"""
        if 7 <= sleep_hours <= 9:
            return "优秀"
        elif 6 <= sleep_hours < 7 or 9 < sleep_hours <= 10:
            return "良好"
        else:
            return "需改善"
    
    def get_sleep_trends(self, days=7):
        """获取睡眠趋势"""
        recent_data = []
        for i in range(days):
            date = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            if date in self.sleep_data:
                recent_data.append(self.sleep_data[date])
        
        if not recent_data:
            return None
            
        avg_hours = sum(d['sleep_hours'] for d in recent_data) / len(recent_data)
        avg_quality = sum(d['quality_score'] for d in recent_data) / len(recent_data)
        
        return {
            'avg_sleep_hours': round(avg_hours, 1),
            'avg_quality_score': round(avg_quality, 1),
            'trend': "改善" if len(recent_data) > 1 and recent_data[0]['quality_score'] > recent_data[-1]['quality_score'] else "稳定"
        }