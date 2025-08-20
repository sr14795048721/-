from models.behavior_analysis import BehaviorAnalysis

class BehaviorService:
    def __init__(self):
        self.analyzer = BehaviorAnalysis()

    def analyze_behavior(self, activity_data):
        """
        分析用户行为数据，返回评分和建议
        """
        result = self.analyzer.analyze(activity_data)
        if 'user_id' not in result and 'user_id' in activity_data:
            result['user_id'] = activity_data['user_id']
        return result