import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import io
import base64
import json
from datetime import datetime, timedelta

class ChartGenerator:
    def __init__(self):
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
        plt.rcParams['axes.unicode_minus'] = False
    
    def create_sleep_chart(self, sleep_data):
        """创建睡眠趋势图"""
        if not sleep_data:
            return None
        
        dates = list(sleep_data.keys())[-7:]  # 最近7天
        hours = [sleep_data[date]['sleep_hours'] for date in dates]
        quality = [sleep_data[date]['quality_score'] for date in dates]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
        
        # 睡眠时长图
        ax1.plot(dates, hours, marker='o', color='#4CAF50')
        ax1.set_title('睡眠时长趋势')
        ax1.set_ylabel('小时')
        ax1.grid(True, alpha=0.3)
        
        # 睡眠质量图
        ax2.plot(dates, quality, marker='s', color='#2196F3')
        ax2.set_title('睡眠质量趋势')
        ax2.set_ylabel('评分')
        ax2.set_xlabel('日期')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def create_leaderboard_chart(self, leaderboard_data):
        """创建排行榜图表"""
        if not leaderboard_data:
            return None
        
        names = [item[0] for item in leaderboard_data[:5]]
        scores = [item[1] for item in leaderboard_data[:5]]
        points = [item[2] for item in leaderboard_data[:5]]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 健康分数排行
        bars1 = ax1.bar(names, scores, color=['#FFD700', '#C0C0C0', '#CD7F32', '#4CAF50', '#2196F3'])
        ax1.set_title('健康分数排行榜', fontsize=14)
        ax1.set_ylabel('健康分数')
        for bar, score in zip(bars1, scores):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                   f'{score:.1f}', ha='center', va='bottom')
        
        # 积分排行
        bars2 = ax2.bar(names, points, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
        ax2.set_title('积分排行榜', fontsize=14)
        ax2.set_ylabel('积分')
        for bar, point in zip(bars2, points):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                   f'{point}', ha='center', va='bottom')
        
        plt.setp(ax1.get_xticklabels(), rotation=45)
        plt.setp(ax2.get_xticklabels(), rotation=45)
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def create_behavior_chart(self, behavior_data):
        """创建行为分析图表"""
        categories = ['屏幕时间', '运动时间', '睡眠质量']
        values = [
            min(behavior_data.get('screen_time', 0) / 8 * 100, 100),
            min(behavior_data.get('exercise', 0) / 60 * 100, 100),
            behavior_data.get('sleep_quality', 70)
        ]
        
        fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(projection='polar'))
        
        angles = [i * 2 * 3.14159 / len(categories) for i in range(len(categories))]
        angles += angles[:1]  # 闭合图形
        values += values[:1]
        
        ax.plot(angles, values, 'o-', linewidth=2, color='#4CAF50')
        ax.fill(angles, values, alpha=0.25, color='#4CAF50')
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 100)
        ax.set_title('健康行为雷达图')
        
        return self._fig_to_base64(fig)
    
    def _fig_to_base64(self, fig):
        """将图表转换为base64字符串"""
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close(fig)
        return f"data:image/png;base64,{img_str}"