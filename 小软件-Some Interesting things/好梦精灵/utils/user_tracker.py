import datetime
import json
import os
from flask import request

class UserTracker:
    def __init__(self):
        self.sessions_file = 'user_sessions.json'
        self.sessions = self.load_sessions()
    
    def load_sessions(self):
        """加载用户会话数据"""
        if os.path.exists(self.sessions_file):
            with open(self.sessions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_sessions(self):
        """保存用户会话数据"""
        with open(self.sessions_file, 'w', encoding='utf-8') as f:
            json.dump(self.sessions, f, ensure_ascii=False, indent=2)
    
    def update_user_session(self, username):
        """更新用户会话信息"""
        now = datetime.datetime.now().isoformat()
        ip_address = self.get_client_ip()
        user_agent = request.headers.get('User-Agent', '')
        
        self.sessions[username] = {
            'last_active': now,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'login_time': self.sessions.get(username, {}).get('login_time', now)
        }
        self.save_sessions()
    
    def get_client_ip(self):
        """获取客户端IP地址"""
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0]
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr
    
    def is_user_online(self, username, timeout_minutes=30):
        """检查用户是否在线"""
        if username not in self.sessions:
            return False
        
        last_active = datetime.datetime.fromisoformat(self.sessions[username]['last_active'])
        now = datetime.datetime.now()
        return (now - last_active).total_seconds() < (timeout_minutes * 60)
    
    def get_user_status(self, username):
        """获取用户状态信息"""
        if username not in self.sessions:
            return {
                'is_online': False,
                'last_active': None,
                'ip_address': None,
                'user_agent': None,
                'login_time': None
            }
        
        session = self.sessions[username]
        return {
            'is_online': self.is_user_online(username),
            'last_active': session['last_active'],
            'ip_address': session['ip_address'],
            'user_agent': session['user_agent'],
            'login_time': session.get('login_time'),
            'device_type': self.get_device_type(session['user_agent'])
        }
    
    def get_device_type(self, user_agent):
        """根据User Agent判断设备类型"""
        if not user_agent:
            return 'Unknown'
        
        user_agent = user_agent.lower()
        if 'android' in user_agent:
            return 'Android'
        elif 'iphone' in user_agent or 'ipad' in user_agent:
            return 'iOS'
        elif 'windows' in user_agent:
            return 'Windows'
        elif 'mac' in user_agent:
            return 'macOS'
        elif 'linux' in user_agent:
            return 'Linux'
        else:
            return 'Other'
    
    def get_all_user_status(self):
        """获取所有用户状态"""
        result = {}
        for username in self.sessions:
            result[username] = self.get_user_status(username)
        return result
    
    def cleanup_old_sessions(self, days=7):
        """清理旧会话数据"""
        cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
        
        to_remove = []
        for username, session in self.sessions.items():
            last_active = datetime.datetime.fromisoformat(session['last_active'])
            if last_active < cutoff:
                to_remove.append(username)
        
        for username in to_remove:
            del self.sessions[username]
        
        if to_remove:
            self.save_sessions()
        
        return len(to_remove)