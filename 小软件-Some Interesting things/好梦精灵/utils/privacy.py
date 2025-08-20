import hashlib
import os
from datetime import datetime, timedelta

class PrivacyProtector:
    def __init__(self):
        self.data_retention_days = 30
    
    def anonymize_user_id(self, user_id):
        """
        匿名化用户ID
        :param user_id: 原始用户ID
        :return: 匿名化后的用户ID
        """
        # 使用SHA-256哈希算法匿名化用户ID
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]
    
    def should_delete_data(self, data_timestamp):
        """
        检查数据是否应该被删除（根据保留策略）
        :param data_timestamp: 数据时间戳
        :return: 是否应该删除
        """
        cutoff_date = datetime.now() - timedelta(days=self.data_retention_days)
        return data_timestamp < cutoff_date
    
    def encrypt_sensitive_data(self, data, key=None):
        """
        加密敏感数据（简单实现）
        :param data: 要加密的数据
        :param key: 加密密钥
        :return: 加密后的数据
        """
        # 在实际应用中，应该使用更安全的加密算法
        if not key:
            key = os.urandom(16)
        
        # 简单的XOR加密（仅作示例，实际应用中应使用更强的加密算法）
        encrypted = ''.join(chr(ord(c) ^ key[i % len(key)]) for i, c in enumerate(data))
        return encrypted, key
    
    def decrypt_sensitive_data(self, encrypted_data, key):
        """
        解密敏感数据
        :param encrypted_data: 加密的数据
        :param key: 解密密钥
        :return: 解密后的数据
        """
        # 简单的XOR解密
        decrypted = ''.join(chr(ord(c) ^ key[i % len(key)]) for i, c in enumerate(encrypted_data))
        return decrypted