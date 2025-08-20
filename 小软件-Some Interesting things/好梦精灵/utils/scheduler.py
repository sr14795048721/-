import schedule
import time
import threading
from datetime import datetime
from .error_reporter import report_generator
from .error_reporter import error_reporter

class AutoReportScheduler:
    def __init__(self):
        self.running = False
        self.thread = None
    
    def start(self):
        """启动定时任务"""
        if self.running:
            return
        
        # 设置定时任务
        schedule.every().day.at("09:00").do(self._generate_daily_report)
        schedule.every().monday.at("10:00").do(self._generate_weekly_report)
        schedule.every().day.at("01:00").do(self._cleanup_old_reports)
        
        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        print("自动报告调度器已启动")
    
    def stop(self):
        """停止定时任务"""
        self.running = False
        schedule.clear()
        print("自动报告调度器已停止")
    
    def _run_scheduler(self):
        """运行调度器"""
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    
    def _generate_daily_report(self):
        """生成日报"""
        try:
            report_file = report_generator.generate_summary_report(days=1)
            print(f"日报已生成: {report_file}")
        except Exception as e:
            error_reporter.capture_error(e, {'task': 'daily_report'})
    
    def _generate_weekly_report(self):
        """生成周报"""
        try:
            report_file = report_generator.generate_summary_report(days=7)
            analysis = report_generator.analyze_errors(days=7)
            print(f"周报已生成: {report_file}")
            print(f"错误趋势: {analysis.get('trend', 'unknown')}")
        except Exception as e:
            error_reporter.capture_error(e, {'task': 'weekly_report'})
    
    def _cleanup_old_reports(self):
        """清理旧报告文件"""
        import os
        import glob
        from datetime import timedelta
        
        try:
            log_dir = report_generator.log_dir
            cutoff_date = datetime.now() - timedelta(days=30)
            
            pattern = os.path.join(log_dir, 'report_*.json')
            for file_path in glob.glob(pattern):
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if file_time < cutoff_date:
                    os.remove(file_path)
                    print(f"已删除旧报告: {file_path}")
        except Exception as e:
            error_reporter.capture_error(e, {'task': 'cleanup_reports'})

# 创建全局调度器实例
auto_scheduler = AutoReportScheduler()