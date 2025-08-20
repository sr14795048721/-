import platform
import subprocess
import re

class DeviceDetector:
    @staticmethod
    def detect_system():
        """检测当前设备系统"""
        system = platform.system().lower()
        
        # 检测是否为Android系统
        is_android = DeviceDetector._is_android_system()
        
        # 检测是否连接了Android设备
        android_connected = DeviceDetector._check_android_device()
        
        return {
            'os': 'android' if is_android else system,
            'is_android': is_android,
            'is_android_connected': android_connected,
            'platform_info': {
                'system': 'Android' if is_android else platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine()
            }
        }
    
    @staticmethod
    def _check_android_device():
        """检查是否连接Android设备"""
        try:
            result = subprocess.run(['adb', 'devices'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # 跳过标题行
                connected_devices = [line for line in lines if 'device' in line and 'offline' not in line]
                return len(connected_devices) > 0
        except Exception:
            pass
        return False
    
    @staticmethod
    def _is_android_system():
        """检测是否为Android系统"""
        try:
            # 检查Android特有文件
            import os
            android_indicators = [
                '/system/build.prop',
                '/system/bin/getprop',
                '/proc/version'
            ]
            
            for indicator in android_indicators:
                if os.path.exists(indicator):
                    if indicator == '/proc/version':
                        with open(indicator, 'r') as f:
                            content = f.read().lower()
                            if 'android' in content:
                                return True
                    else:
                        return True
            
            # 检查环境变量
            if os.environ.get('ANDROID_ROOT') or os.environ.get('ANDROID_DATA'):
                return True
                
        except Exception:
            pass
        return False
    
    @staticmethod
    def get_optimal_data_source():
        """获取最佳数据源"""
        detection = DeviceDetector.detect_system()
        
        if detection['is_android']:
            return 'android_native'
        elif detection['is_android_connected']:
            return 'android_adb'
        elif detection['os'] == 'windows':
            return 'windows'
        else:
            return 'default'