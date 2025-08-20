import unittest
import sys
import os

# Add the parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from models.sleep_predictor import SleepPredictor
from models.behavior_analysis import BehaviorAnalysis

class TestSleepPredictor(unittest.TestCase):
    def setUp(self):
        self.predictor = SleepPredictor()
    
    def test_predict_quality_without_training(self):
        quality = self.predictor.predict_quality(8)
        self.assertEqual(quality, 7.0)  # 默认值
    
    def test_train_and_predict(self):
        # 训练模型
        sleep_data = [6, 7, 8, 9, 10]
        quality_scores = [5.0, 6.5, 7.0, 8.0, 9.0]
        self.predictor.train(sleep_data, quality_scores)
        
        # 预测
        quality = self.predictor.predict_quality(7.5)
        self.assertIsInstance(quality, float)

class TestBehaviorAnalysis(unittest.TestCase):
    def setUp(self):
        self.analyzer = BehaviorAnalysis()
    
    def test_analyze_good_behavior(self):
        activity_data = {
            'screen_time': 2,
            'exercise': 45,
            'bedtime': 22
        }
        result = self.analyzer.analyze(activity_data)
        self.assertEqual(result['score'], 100)
        self.assertEqual(len(result['advice']), 0)
    
    def test_analyze_poor_behavior(self):
        activity_data = {
            'screen_time': 5,
            'exercise': 15,
            'bedtime': 24
        }
        result = self.analyzer.analyze(activity_data)
        self.assertEqual(result['score'], 70)
        self.assertEqual(len(result['advice']), 3)

if __name__ == '__main__':
    unittest.main()