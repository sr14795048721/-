import json
import os
from datetime import datetime
from typing import List, Dict

class ChatService:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.messages_file = os.path.join(self.data_dir, 'chat_messages.json')
        self.online_users = set()
        self.messages = self.load_messages()
    
    def load_messages(self) -> List[Dict]:
        """加载聊天消息"""
        if os.path.exists(self.messages_file):
            try:
                with open(self.messages_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_messages(self):
        """保存聊天消息"""
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.messages_file, 'w', encoding='utf-8') as f:
            json.dump(self.messages[-100:], f, ensure_ascii=False, indent=2)  # 只保留最近100条
    
    def add_message(self, username: str, message: str) -> Dict:
        """添加消息"""
        msg = {
            'id': len(self.messages) + 1,
            'username': username,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.messages.append(msg)
        self.save_messages()
        return msg
    
    def get_recent_messages(self, limit: int = 50) -> List[Dict]:
        """获取最近的消息"""
        return self.messages[-limit:]
    
    def join_room(self, username: str):
        """用户加入聊天室"""
        self.online_users.add(username)
    
    def leave_room(self, username: str):
        """用户离开聊天室"""
        self.online_users.discard(username)
    
    def get_online_users(self) -> List[str]:
        """获取在线用户列表"""
        return list(self.online_users)
    
    def get_online_count(self) -> int:
        """获取在线用户数量"""
        return len(self.online_users)