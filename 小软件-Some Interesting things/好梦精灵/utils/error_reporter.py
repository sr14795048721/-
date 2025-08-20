# 创建全局实例供外部导入
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict, Counter

class ReportGenerator:
    def __init__(self, log_dir='logs'):
        self.log_dir = log_dir
        self.ensure_log_dir()
    
    def ensure_log_dir(self):
        """确保日志目录存在"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def generate_summary_report(self, days=7):
        """生成指定天数的摘要报告"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        report_data = {
            'report_period': f"{start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}",
            'generated_at': datetime.now().isoformat(),
            'summary': self._generate_summary(days),
            'details': self._get_error_details(days)
        }
        
        report_file = os.path.join(self.log_dir, f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return report_file
    
    def _generate_summary(self, days):
        """生成摘要统计"""
        errors = self._get_recent_errors(days)
        
        return {
            'total_errors': len(errors),
            'error_types': dict(Counter(error.get('type', 'Unknown') for error in errors)),
            'daily_counts': self._get_daily_error_counts(errors),
            'most_common_errors': self._get_most_common_errors(errors)
        }
    
    def _get_recent_errors(self, days):
        """获取最近指定天数的错误"""
        cutoff_date = datetime.now() - timedelta(days=days)
        errors = []
        
        error_file = os.path.join(self.log_dir, 'errors.json')
        if os.path.exists(error_file):
            try:
                with open(error_file, 'r', encoding='utf-8') as f:
                    all_errors = json.load(f)
                    for error in all_errors:
                        error_time = datetime.fromisoformat(error['timestamp'])
                        if error_time >= cutoff_date:
                            errors.append(error)
            except Exception:
                pass
        
        return errors
    
    def _get_daily_error_counts(self, errors):
        """获取每日错误统计"""
        daily_counts = defaultdict(int)
        for error in errors:
            date = error['timestamp'][:10]  # 取日期部分
            daily_counts[date] += 1
        return dict(daily_counts)
    
    def _get_most_common_errors(self, errors, limit=5):
        """获取最常见的错误"""
        error_messages = [error.get('message', '') for error in errors]
        return dict(Counter(error_messages).most_common(limit))
    
    def _get_error_details(self, days):
        """获取错误详细信息"""
        errors = self._get_recent_errors(days)
        return errors[-10:]  # 返回最近10个错误的详细信息
    
    def analyze_errors(self, days=7):
        """分析错误趋势"""
        errors = self._get_recent_errors(days)
        
        if not errors:
            return {'status': 'no_errors', 'message': '指定期间内无错误记录'}
        
        analysis = {
            'trend': self._analyze_trend(errors),
            'severity': self._analyze_severity(errors),
            'recommendations': self._generate_recommendations(errors)
        }
        
        return analysis
    
    def _analyze_trend(self, errors):
        """分析错误趋势"""
        if len(errors) < 2:
            return 'insufficient_data'
        
        # 简单的趋势分析：比较前半段和后半段的错误数量
        mid_point = len(errors) // 2
        first_half = errors[:mid_point]
        second_half = errors[mid_point:]
        
        if len(second_half) > len(first_half) * 1.2:
            return 'increasing'
        elif len(second_half) < len(first_half) * 0.8:
            return 'decreasing'
        else:
            return 'stable'
    
    def _analyze_severity(self, errors):
        """分析错误严重程度"""
        severity_counts = Counter(error.get('severity', 'medium') for error in errors)
        total = len(errors)
        
        return {
            'high': severity_counts.get('high', 0) / total * 100,
            'medium': severity_counts.get('medium', 0) / total * 100,
            'low': severity_counts.get('low', 0) / total * 100
        }
    
    def _generate_recommendations(self, errors):
        """生成改进建议"""
        recommendations = []
        
        # 基于错误类型生成建议
        error_types = Counter(error.get('type', 'Unknown') for error in errors)
        
        if error_types.get('ValidationError', 0) > len(errors) * 0.3:
            recommendations.append('建议加强输入验证和数据校验')
        
        if error_types.get('DatabaseError', 0) > 0:
            recommendations.append('建议检查数据库连接和查询优化')
        
        if error_types.get('NetworkError', 0) > 0:
            recommendations.append('建议增加网络重试机制和超时处理')
        
        if not recommendations:
            recommendations.append('系统运行良好，建议继续监控')
        
        return recommendations

    def capture_error(self, error, context=None):
        """
        记录错误到 logs/error.log，附加上下文信息
        """
        log_path = os.path.join(self.log_dir, 'error.log')
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().isoformat()}] 错误: {str(error)}\n")
            if context:
                f.write(f"上下文: {str(context)}\n")

def auto_report_error(error):
    """
    自动错误自动上报：将错误信息追加写入 logs/error.log 文件
    """
    log_path = os.path.join('logs', 'error.log')
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now().isoformat()}] 自动上报错误: {error}\n")
    print(f"自动上报错误: {error}")

error_reporter = ReportGenerator()
report_generator = ReportGenerator()