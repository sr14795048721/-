import unittest
import sys
import os
import json

# Add the parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from services.sleep_service import SleepService
from services.behavior_service import BehaviorService
from services.incentive_service import IncentiveService

class TestSleepService(unittest.TestCase):
    def setUp(self):
        self.sleep_service = SleepService()
    
    def test_analyze_sleep(self):
        result = self.sleep_service.analyze_sleep("test_user", 8, "22:30")
        self.assertIn('predicted_quality', result)
        self.assertIn('recommendation', result)
        self.assertEqual(result['user_id'], "test_user")
        self.assertEqual(result['sleep_hours'], 8)

class TestBehaviorService(unittest.TestCase):
    def setUp(self):
        self.behavior_service = BehaviorService()
    
    def test_analyze_behavior(self):
        activity_data = {
            'screen_time': 2,
            'exercise': 45,
            'bedtime': 22
        }
        result = self.behavior_service.analyze_behavior(activity_data)
        self.assertIn('score', result)
        self.assertIn('advice', result)

class TestIncentiveService(unittest.TestCase):
    def setUp(self):
        self.incentive_service = IncentiveService("test_data")
    
    def tearDown(self):
        # 清理测试数据
        import shutil
        if os.path.exists("test_data"):
            shutil.rmtree("test_data")
    
    def test_add_points(self):
        points = self.incentive_service.add_points("test_user", 10, "测试积分")
        self.assertEqual(points, 10)
        
        # 再次添加积分
        points = self.incentive_service.add_points("test_user", 5, "测试积分2")
        self.assertEqual(points, 15)
    
    def test_get_user_points(self):
        # 添加积分
        self.incentive_service.add_points("test_user", 10, "测试积分")
        
        # 获取积分
        points = self.incentive_service.get_user_points("test_user")
        self.assertEqual(points, 10)
    
    def test_award_badge(self):
        result = self.incentive_service.award_badge("test_user", "test_badge")
        self.assertTrue(result)
        
        # 再次授予相同徽章应该返回False
        result = self.incentive_service.award_badge("test_user", "test_badge")
        self.assertFalse(result)
    
    def test_get_user_badges(self):
        # 授予徽章
        self.incentive_service.award_badge("test_user", "test_badge1")
        self.incentive_service.award_badge("test_user", "test_badge2")
        
        # 获取徽章
        badges = self.incentive_service.get_user_badges("test_user")
        self.assertIn("test_badge1", badges)
        self.assertIn("test_badge2", badges)

if __name__ == '__main__':
    unittest.main()