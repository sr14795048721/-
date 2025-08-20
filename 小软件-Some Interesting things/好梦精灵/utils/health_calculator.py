import datetime

class HealthCalculator:
    @staticmethod
    def calculate_sleep_score(sleep_hours, bedtime):
        """计算睡眠健康分数 - 优化版"""
        try:
            bedtime_parts = bedtime.split(':')
            bedtime_hour = float(bedtime_parts[0]) + float(bedtime_parts[1])/60
            
            # 理想睡眠窗口计算（21:00-23:30为最佳入睡时间）
            if 21 <= bedtime_hour <= 23.5:
                sleep_window = 24 - bedtime_hour + 7  # 到早上7点
                efficiency_bonus = 1.2  # 最佳时间段奖励
            elif bedtime_hour >= 20:
                sleep_window = 24 - bedtime_hour + 7
                efficiency_bonus = 1.0
            else:  # 凌晨入睡
                sleep_window = 7 - bedtime_hour if bedtime_hour < 7 else 1
                efficiency_bonus = 0.8  # 熬夜惩罚
            
            # 基础分数计算
            base_score = (sleep_hours / max(sleep_window, 1)) * 10
            
            # 睡眠时长调整
            if 7 <= sleep_hours <= 9:
                duration_bonus = 1.1  # 理想睡眠时长奖励
            elif 6 <= sleep_hours < 7 or 9 < sleep_hours <= 10:
                duration_bonus = 1.0
            else:
                duration_bonus = 0.8  # 过短或过长惩罚
            
            final_score = min(10, base_score * efficiency_bonus * duration_bonus)
            return round(final_score, 1)
            
        except Exception:
            return 5.0  # 默认分数
    
    @staticmethod
    def calculate_behavior_score(screen_time, exercise_time):
        """计算行为健康分数 - 优化版"""
        try:
            if screen_time <= 0:
                return 10.0  # 无屏幕使用给满分
            
            # 基础比例分数
            ratio_score = min(10, (exercise_time / screen_time) * 10)
            
            # 屏幕时间惩罚
            if screen_time > 8:
                screen_penalty = 0.5  # 重度使用惩罚
            elif screen_time > 4:
                screen_penalty = 0.8  # 中度使用惩罚
            else:
                screen_penalty = 1.0  # 正常使用
            
            # 运动时间奖励
            if exercise_time >= 60:
                exercise_bonus = 1.2  # 充足运动奖励
            elif exercise_time >= 30:
                exercise_bonus = 1.1  # 适量运动奖励
            else:
                exercise_bonus = 1.0
            
            final_score = min(10, ratio_score * screen_penalty * exercise_bonus)
            return round(final_score, 1)
            
        except Exception:
            return 5.0  # 默认分数
    
    @staticmethod
    def calculate_comprehensive_score(sleep_score, behavior_score, days=7):
        """计算综合健康分数"""
        # 睡眠和行为分数加权平均
        comprehensive = (sleep_score * 0.6 + behavior_score * 0.4)
        
        # 根据数据完整性调整
        if sleep_score > 0 and behavior_score > 0:
            completeness_bonus = 1.0
        else:
            completeness_bonus = 0.8  # 数据不完整惩罚
        
        return round(min(10, comprehensive * completeness_bonus), 1)
    
    @staticmethod
    def get_health_level(score):
        """获取健康等级"""
        if score >= 9:
            return {"level": "优秀", "color": "#4CAF50", "icon": "🏆"}
        elif score >= 7:
            return {"level": "良好", "color": "#8BC34A", "icon": "👍"}
        elif score >= 5:
            return {"level": "一般", "color": "#FFC107", "icon": "⚠️"}
        elif score >= 3:
            return {"level": "较差", "color": "#FF9800", "icon": "📉"}
        else:
            return {"level": "很差", "color": "#F44336", "icon": "🚨"}