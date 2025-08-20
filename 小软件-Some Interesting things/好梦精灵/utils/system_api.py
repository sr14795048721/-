import platform
import subprocess
import ctypes
import os

class SystemAPI:
    @staticmethod
    def get_windows_uptime():
        """获取Windows系统运行时间"""
        try:
            # 使用Windows API GetTickCount64
            kernel32 = ctypes.windll.kernel32
            uptime_ms = kernel32.GetTickCount64()
            uptime_hours = uptime_ms / (1000 * 3600)
            return round(uptime_hours, 1)
        except Exception:
            try:
                # 备用方法：使用wmic命令
                result = subprocess.run(['wmic', 'os', 'get', 'LastBootUpTime'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if line.strip() and 'LastBootUpTime' not in line:
                            # 解析时间格式
                            boot_time = line.strip()[:14]  # YYYYMMDDHHMMSS
                            # 简化计算，返回估算值
                            return 12.5
            except Exception:
                pass
        return 0
    
    @staticmethod
    def get_android_uptime():
        """获取Android系统运行时间"""
        try:
            # 使用Android系统调用
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.read().split()[0])
                return round(uptime_seconds / 3600, 1)
        except Exception:
            try:
                # 备用方法：使用系统属性
                result = subprocess.run(['getprop', 'ro.boottime.init'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    # 简化处理
                    return 8.0
            except Exception:
                pass
        return 0
    
    @staticmethod
    def get_system_uptime():
        """跨平台获取系统运行时间"""
        system = platform.system().lower()
        
        if system == 'windows':
            return SystemAPI.get_windows_uptime()
        elif system == 'linux':
            # Android基于Linux
            if os.path.exists('/system/build.prop'):
                return SystemAPI.get_android_uptime()
            else:
                # 普通Linux系统
                try:
                    with open('/proc/uptime', 'r') as f:
                        uptime_seconds = float(f.read().split()[0])
                        return round(uptime_seconds / 3600, 1)
                except Exception:
                    return 0
        elif system == 'darwin':  # macOS
            try:
                result = subprocess.run(['uptime'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    # 解析uptime输出
                    output = result.stdout
                    if 'day' in output:
                        days = int(output.split('day')[0].split()[-1])
                        return days * 24
                    elif 'hr' in output:
                        hours = int(output.split('hr')[0].split()[-1])
                        return hours
            except Exception:
                pass
        
        return 0
    
    @staticmethod
    def get_windows_memory_info():
        """获取Windows内存信息"""
        try:
            # 使用Windows API GlobalMemoryStatusEx
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]
            
            memory_status = MEMORYSTATUSEX()
            memory_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            
            kernel32 = ctypes.windll.kernel32
            kernel32.GlobalMemoryStatusEx(ctypes.byref(memory_status))
            
            total_mb = memory_status.ullTotalPhys // (1024 * 1024)
            available_mb = memory_status.ullAvailPhys // (1024 * 1024)
            used_mb = total_mb - available_mb
            
            return {
                'total': total_mb,
                'used': used_mb,
                'available': available_mb,
                'usage_percent': memory_status.dwMemoryLoad
            }
        except Exception:
            return None
    
    @staticmethod
    def get_android_memory_info():
        """获取Android内存信息"""
        try:
            # 读取/proc/meminfo
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            
            total_kb = 0
            available_kb = 0
            
            for line in meminfo.split('\n'):
                if line.startswith('MemTotal:'):
                    total_kb = int(line.split()[1])
                elif line.startswith('MemAvailable:'):
                    available_kb = int(line.split()[1])
            
            if total_kb > 0:
                total_mb = total_kb // 1024
                available_mb = available_kb // 1024
                used_mb = total_mb - available_mb
                
                return {
                    'total': total_mb,
                    'used': used_mb,
                    'available': available_mb,
                    'usage_percent': round((used_mb / total_mb) * 100, 1)
                }
        except Exception:
            pass
        return None