try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None
import io
import base64
from datetime import datetime

class DataVisualizer:
    def __init__(self):
        if MATPLOTLIB_AVAILABLE:
            # 设置中文字体支持
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False

    def create_sleep_chart(self, sleep_data):
        """
        创建睡眠数据图表
        :param sleep_data: 睡眠数据列表，每个元素包含日期和睡眠质量
        :return: base64编码的图片
        """
        if not MATPLOTLIB_AVAILABLE:
            return None
            
        if not sleep_data:
            return None
            
        dates = [datetime.strptime(d['date'], '%Y-%m-%d') for d in sleep_data]
        qualities = [d['quality'] for d in sleep_data]
        
        plt.figure(figsize=(10, 6))
        plt.plot(dates, qualities, marker='o', linewidth=2, markersize=8)
        plt.title('睡眠质量趋势', fontsize=16)
        plt.xlabel('日期', fontsize=12)
        plt.ylabel('睡眠质量', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # 格式化x轴日期显示
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # 转换为base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return img_str

    def create_behavior_chart(self, behavior_scores):
        """
        创建行为分析图表
        :param behavior_scores: 行为评分数据
        :return: base64编码的图片
        """
        if not MATPLOTLIB_AVAILABLE:
            return None
            
        if not behavior_scores:
            return None
            
        dates = [datetime.strptime(d['date'], '%Y-%m-%d') for d in behavior_scores]
        scores = [d['score'] for d in behavior_scores]
        
        plt.figure(figsize=(10, 6))
        plt.bar(range(len(dates)), scores, color='#667eea')
        plt.title('健康行为评分', fontsize=16)
        plt.xlabel('日期', fontsize=12)
        plt.ylabel('评分', fontsize=12)
        plt.xticks(range(len(dates)), [d.strftime('%m-%d') for d in dates], rotation=45)
        plt.ylim(0, 100)
        
        # 在柱状图上显示数值
        for i, score in enumerate(scores):
            plt.text(i, score + 1, str(score), ha='center', va='bottom')
        
        plt.tight_layout()
        
        # 转换为base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        plt.close()
        
        return img_str