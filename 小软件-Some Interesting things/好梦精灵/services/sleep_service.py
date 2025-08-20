from models.sleep_predictor import SleepPredictor
from utils.error_reporter import auto_report_error

class SleepService:
    def __init__(self):
        self.predictor = SleepPredictor()
    
    @auto_report_error
    def analyze_sleep(self, user_id, sleep_hours, bedtime):
        quality = self.predictor.predict_quality(sleep_hours)
        return {
            'user_id': user_id,
            'sleep_hours': sleep_hours,
            'bedtime': bedtime,
            'predicted_quality': quality,
            'recommendation': self._get_recommendation(sleep_hours)
        }
    
    def _get_recommendation(self, hours):
        if hours < 6:
            return "建议增加睡眠时间，保证充足休息"
        elif hours > 9:
            return "睡眠时间可能过长，建议适当调整"
        return "睡眠时间良好，继续保持"