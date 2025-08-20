import psutil
import time
from typing import Dict, Any

class SystemMonitor:
    def __init__(self):
        self.last_cpu_times = psutil.cpu_times()
        self.last_time = time.time()
    
    def get_cpu_usage(self) -> float:
        """
        获取CPU使用率，采用更精确的计算方式
        """
        current_times = psutil.cpu_times()
        current_time = time.time()
        
        # 计算时间间隔
        time_delta = current_time - self.last_time
        
        # 计算CPU使用率
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # 更新上次记录
        self.last_cpu_times = current_times
        self.last_time = current_time
        
        return round(cpu_percent, 2)
    
    def get_memory_info(self) -> Dict[str, Any]:
        """
        获取内存信息
        """
        memory = psutil.virtual_memory()
        return {
            'total': memory.total,
            'available': memory.available,
            'used': memory.used,
            'free': memory.free,
            'percent': round(memory.percent, 2)
        }
    
    def get_disk_usage(self, path: str = '/') -> Dict[str, Any]:
        """
        获取磁盘使用情况
        """
        if psutil.WINDOWS:
            path = 'C:\\'
        disk = psutil.disk_usage(path)
        return {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': round((disk.used / disk.total) * 100, 2) if disk.total > 0 else 0
        }
    
    def get_network_io(self) -> Dict[str, Any]:
        """
        获取网络IO信息
        """
        net_io = psutil.net_io_counters()
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv
        }
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        获取完整的系统信息
        """
        return {
            'cpu_usage': self.get_cpu_usage(),
            'memory': self.get_memory_info(),
            'disk': self.get_disk_usage(),
            'network': self.get_network_io(),
            'boot_time': psutil.boot_time(),
            'process_count': len(psutil.pids())
        }

# 全局实例
system_monitor = SystemMonitor()

def get_system_info() -> Dict[str, Any]:
    """
    获取系统信息的便捷函数
    """
    return system_monitor.get_system_info()