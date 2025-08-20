class BehaviorAnalysis:
    def analyze(self, data):
        from utils.device_detector import DeviceDetector
        from utils.health_calculator import HealthCalculator
        
        data_source = DeviceDetector.get_optimal_data_source()
        
        if data_source == 'android_native':
            from utils.android_native import AndroidNative
            screen_time = AndroidNative.get_screen_time()
            steps = AndroidNative.get_step_count()
            exercise_time = AndroidNative.calculate_exercise_time(steps)
        elif data_source == 'android_adb':
            from utils.android_api import AndroidAPI
            screen_time = AndroidAPI.get_screen_time()
            steps = AndroidAPI.get_step_count()
            exercise_time = AndroidAPI.calculate_exercise_time(steps)
        else:
            # 使用系统数据或默认值
            from utils.android_system import CrossPlatformSystem
            sys_info = CrossPlatformSystem.get_system_info()
            screen_time = sys_info.get('screen_time_hours', 2.5)
            exercise_time = data.get('exercise', 30)  # 用户输入的运动时间
            steps = int(exercise_time * 100)  # 估算步数
        
        # 使用优化的健康计算器
        score = HealthCalculator.calculate_behavior_score(screen_time, exercise_time)
        health_level = HealthCalculator.get_health_level(score)
            
        return {
            'score': score,
            'screen_time': screen_time,
            'exercise_time': exercise_time,
            'steps': steps,
            'health_level': health_level,
            'data_source': data_source
        }