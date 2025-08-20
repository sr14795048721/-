import os
import subprocess
import json

class AndroidNative:
    @staticmethod
    def get_screen_time():
        """获取Android原生屏幕使用时间"""
        try:
            # 使用Android原生命令
            result = subprocess.run(['dumpsys', 'usagestats'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # 解析屏幕使用时间
                lines = result.stdout.split('\n')
                total_time = 0
                for line in lines:
                    if 'totalTimeInForeground' in line:
                        try:
                            time_ms = int(line.split('=')[1].strip())
                            total_time += time_ms
                        except:
                            continue
                return round(total_time / (1000 * 3600), 1)
        except Exception:
            pass
        return 3.0  # Android默认值
    
    @staticmethod
    def get_step_count():
        """获取Android原生步数"""
        try:
            # 使用传感器服务
            result = subprocess.run(['dumpsys', 'sensorservice'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'step' in line.lower() and 'count' in line.lower():
                        try:
                            import re
                            match = re.search(r'(\d+)', line)
                            if match:
                                return min(int(match.group(1)), 20000)
                        except:
                            continue
        except Exception:
            pass
        return 6000  # Android默认值
    
    @staticmethod
    def get_battery_info():
        """获取Android电池信息"""
        try:
            result = subprocess.run(['dumpsys', 'battery'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'level:' in line:
                        try:
                            return int(line.split(':')[1].strip())
                        except:
                            continue
        except Exception:
            pass
        return 80  # 默认电量
    
    @staticmethod
    def get_device_info():
        """获取Android设备信息"""
        try:
            # 获取设备属性
            props = {}
            result = subprocess.run(['getprop'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if '[ro.build.version.release]' in line:
                        props['android_version'] = line.split(']:')[1].strip(' []')
                    elif '[ro.product.model]' in line:
                        props['model'] = line.split(']:')[1].strip(' []')
            
            return props
        except Exception:
            return {'android_version': 'Unknown', 'model': 'Android Device'}
    
    @staticmethod
    def calculate_exercise_time(steps):
        """根据步数计算运动时间"""
        # Android设备步数转运动时间
        minutes = steps / 120  # Android用户平均步频
        return min(minutes, 150)  # 最大2.5小时