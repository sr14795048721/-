import platform
import os
import time
import datetime

class SystemInfo:
    @staticmethod
    def get_os_info():
        """
        获取操作系统信息
        """
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'architecture': platform.architecture()[0],
            'machine': platform.machine(),
            'processor': platform.processor()
        }

    @staticmethod
    def get_uptime():
        """
        获取系统运行时间（单位：秒、分钟、小时、天）
        """
        if platform.system() == 'Windows':
            # Windows下通过系统启动时间计算
            import ctypes
            import sys
            if sys.getwindowsversion().major >= 6:
                GetTickCount64 = ctypes.windll.kernel32.GetTickCount64
                uptime_ms = GetTickCount64()
            else:
                GetTickCount = ctypes.windll.kernel32.GetTickCount
                uptime_ms = GetTickCount()
            uptime_sec = int(uptime_ms // 1000)
        else:
            # Linux/macOS下通过 /proc/uptime 或系统启动时间
            try:
                with open('/proc/uptime', 'r') as f:
                    uptime_sec = int(float(f.readline().split()[0]))
            except Exception:
                try:
                    import psutil
                    uptime_sec = int(time.time() - psutil.boot_time())
                except ImportError:
                    # 如果psutil未安装，则使用当前时间作为默认值
                    uptime_sec = int(time.time())
        return {
            'seconds': uptime_sec,
            'minutes': uptime_sec // 60,
            'hours': uptime_sec // 3600,
            'days': uptime_sec // 86400
        }

    @staticmethod
    def get_boot_time():
        """
        获取系统启动时间
        """
        if platform.system() == 'Windows':
            boot_time = datetime.datetime.now() - datetime.timedelta(seconds=SystemInfo.get_uptime()['seconds'])
        else:
            try:
                import psutil
                boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
            except Exception:
                boot_time = None
        return boot_time

    @staticmethod
    def get_app_uptime():
        """
        获取应用运行时间
        """
        try:
            import psutil
            # 获取当前进程
            current_process = psutil.Process(os.getpid())
            # 获取进程创建时间
            create_time = current_process.create_time()
            # 计算运行时间
            uptime_sec = int(time.time() - create_time)
            
            return {
                'seconds': uptime_sec,
                'minutes': uptime_sec // 60,
                'hours': uptime_sec // 3600,
                'days': uptime_sec // 86400
            }
        except Exception:
            # 如果无法获取进程信息，返回None
            return None

    @staticmethod
    def get_app_start_time():
        """
        获取应用启动时间
        """
        try:
            import psutil
            # 获取当前进程
            current_process = psutil.Process(os.getpid())
            # 获取进程创建时间
            create_time = current_process.create_time()
            # 转换为datetime对象
            start_time = datetime.datetime.fromtimestamp(create_time)
            return start_time
        except Exception:
            # 如果无法获取进程信息，返回None
            return None

# 示例用法
if __name__ == '__main__':
    print('操作系统信息:', SystemInfo.get_os_info())
    print('系统运行时间:', SystemInfo.get_uptime())
    print('系统启动时间:', SystemInfo.get_boot_time())
    print('应用运行时间:', SystemInfo.get_app_uptime())
    print('应用启动时间:', SystemInfo.get_app_start_time())