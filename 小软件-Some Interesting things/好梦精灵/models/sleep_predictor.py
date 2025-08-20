import numpy as np
from sklearn.linear_model import LinearRegression

class SleepPredictor:
    def __init__(self):
        self.model = LinearRegression()
        self.is_trained = False
    
    def train(self, sleep_data, quality_scores):
        X = np.array(sleep_data).reshape(-1, 1)
        y = np.array(quality_scores)
        self.model.fit(X, y)
        self.is_trained = True
    
    def predict_quality(self, sleep_hours):
        if not self.is_trained:
            # 基于睡眠时长的简单评分算法
            if sleep_hours < 4:
                return 3.0
            elif sleep_hours < 6:
                return 5.0
            elif sleep_hours <= 8:
                return 8.0 + (sleep_hours - 6) * 0.5
            elif sleep_hours <= 9:
                return 9.0
            else:
                return 7.0 - (sleep_hours - 9) * 0.5
        return max(1.0, min(10.0, self.model.predict([[sleep_hours]])[0]))