import json
import os
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class UserService:
    def __init__(self):
        self.users_file = 'users.json'
        self.users = self.load_users()
        # 微信配置
        self.wechat_app_id = 'your_wechat_app_id'
        self.wechat_app_secret = 'your_wechat_app_secret'
    
    def load_users(self):
        """加载用户数据"""
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_users(self):
        """保存用户数据"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)
    
    def register_user(self, username, password):
        """用户注册"""
        if username in self.users:
            return {'success': False, 'message': '用户已存在'}
        
        # 检查是否为管理员账号
        is_admin = username == 'admin'
        
        self.users[username] = {
            'password_hash': generate_password_hash(password),
            'created_at': datetime.datetime.now().isoformat(),
            'health_score': 0,
            'sleep_data': {},
            'behavior_data': {},
            'is_admin': is_admin,
            'wechat_openid': None,
            'wechat_info': {}
        }
        self.save_users()
        return {'success': True, 'message': '注册成功'}
    
    def login_user(self, username, password):
        """用户登录"""
        if username not in self.users:
            return {'success': False, 'message': '用户不存在'}
        
        if check_password_hash(self.users[username]['password_hash'], password):
            return {'success': True, 'user_id': username}
        return {'success': False, 'message': '密码错误'}
    
    def get_user_info(self, username):
        """获取用户信息"""
        if username in self.users:
            user_data = self.users[username].copy()
            user_data.pop('password_hash', None)
            return user_data
        return None
    
    def clear_user_data(self, username):
        """清除用户数据（仅管理员）"""
        if username in self.users and self.users[username].get('is_admin'):
            for user in self.users.values():
                if not user.get('is_admin'):
                    user['health_score'] = 0
                    user['sleep_data'] = {}
                    user['behavior_data'] = {}
            self.save_users()
            return True
        return False
    
    def add_health_score(self, username, score):
        """累加用户健康分数"""
        if username in self.users:
            self.users[username]['health_score'] += score
            self.save_users()
            return self.users[username]['health_score']
        return 0
    
    def reset_all_scores(self):
        """重置所有用户健康分数"""
        for username, data in self.users.items():
            if not data.get('is_admin', False):
                data['health_score'] = 0
        self.save_users()
    
    def bind_wechat(self, username, openid, wechat_info):
        """绑定微信账号"""
        if username in self.users:
            self.users[username]['wechat_openid'] = openid
            self.users[username]['wechat_info'] = wechat_info
            self.save_users()
            return True
        return False
    
    def get_wechat_users(self):
        """获取已绑定微信的用户"""
        wechat_users = []
        for username, data in self.users.items():
            if data.get('wechat_openid') and not data.get('is_admin', False):
                wechat_users.append({
                    'username': username,
                    'openid': data['wechat_openid'],
                    'wechat_info': data.get('wechat_info', {})
                })
        return wechat_users
    
    def get_leaderboard(self, limit=10):
        """获取排行榜"""
        # 过滤非管理员用户
        regular_users = [
            (name, data['health_score']) 
            for name, data in self.users.items() 
            if not data.get('is_admin', False)
        ]
        
        # 按健康分数排序
        sorted_users = sorted(regular_users, key=lambda x: x[1], reverse=True)
        return sorted_users[:limit]