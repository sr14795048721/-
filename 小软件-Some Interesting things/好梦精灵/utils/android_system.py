import datetime
import json
import subprocess
import platform

class AndroidSystemInfo:
    @staticmethod
    def get_screen_time():
        """获取安卓屏幕使用时间"""
        try:
            # 使用adb命令获取屏幕使用统计
            result = subprocess.run(['adb', 'shell', 'dumpsys', 'usagestats'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # 解析屏幕使用时间（简化版）
                lines = result.stdout.split('\n')
                total_time = 0
                for line in lines:
                    if 'totalTimeInForeground' in line:
                        time_ms = int(line.split('=')[1].strip())
                        total_time += time_ms
                return round(total_time / (1000 * 3600), 1)  # 转换为小时
        except Exception:
            pass
        return 0
    
    @staticmethod
    def get_app_usage():
        """获取应用使用统计"""
        try:
            result = subprocess.run(['adb', 'shell', 'dumpsys', 'package'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return {"app_count": len(result.stdout.split('Package [')), "status": "active"}
        except Exception:
            pass
        return {"app_count": 0, "status": "unknown"}
    
    @staticmethod
    def get_battery_info():
        """获取电池信息"""
        try:
            result = subprocess.run(['adb', 'shell', 'dumpsys', 'battery'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                battery_level = 0
                for line in lines:
                    if 'level:' in line:
                        battery_level = int(line.split(':')[1].strip())
                        break
                return battery_level
        except Exception:
            pass
        return 0

class CrossPlatformSystem:
    @staticmethod
    def get_system_info():
        """跨平台系统信息获取"""
        from .device_detector import DeviceDetector
        
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data_source = DeviceDetector.get_optimal_data_source()
        detection = DeviceDetector.detect_system()
        
        base_info = {
            'current_time': current_time,
            'os': detection['platform_info']['system'],
            'version': detection['platform_info']['release'],
            'data_source': data_source
        }
        
        if data_source == 'android_native':
            from utils.android_native import AndroidNative
            android_info = AndroidNative()
            device_info = android_info.get_device_info()
            base_info.update({
                'screen_time_hours': android_info.get_screen_time(),
                'app_runtime_hours': 0.1,
                'system_uptime_hours': 24.0,
                'battery_level': android_info.get_battery_info(),
                'device_model': device_info.get('model', 'Android Device'),
                'android_version': device_info.get('android_version', 'Unknown')
            })
        elif data_source == 'android_adb':
            android_info = AndroidSystemInfo()
            base_info.update({
                'screen_time_hours': android_info.get_screen_time(),
                'app_runtime_hours': 0.1,
                'system_uptime_hours': 24.0,
                'battery_level': android_info.get_battery_info()
            })
        elif data_source == 'windows':
            from .system_info import SystemInfo
            win_info = SystemInfo.get_system_info()
            base_info.update(win_info)
        else:
            base_info.update({
                'screen_time_hours': 2.5,
                'app_runtime_hours': 0.1,
                'system_uptime_hours': 12.0
            })
        
        return base_info