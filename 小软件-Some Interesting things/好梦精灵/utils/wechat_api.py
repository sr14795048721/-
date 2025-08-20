import requests
import json
import hashlib
import time

class WeChatAPI:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.token_expires = 0
    
    def get_access_token(self):
        """获取微信访问令牌"""
        if self.access_token and time.time() < self.token_expires:
            return self.access_token
        
        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            'grant_type': 'client_credential',
            'appid': self.app_id,
            'secret': self.app_secret
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'access_token' in data:
                self.access_token = data['access_token']
                self.token_expires = time.time() + data['expires_in'] - 300  # 提前5分钟过期
                return self.access_token
        except Exception as e:
            print(f"获取微信访问令牌失败: {e}")
        
        return None
    
    def get_user_step_info(self, openid):
        """获取用户微信运动步数"""
        access_token = self.get_access_token()
        if not access_token:
            return None
        
        url = "https://api.weixin.qq.com/cgi-bin/user/info"
        params = {
            'access_token': access_token,
            'openid': openid,
            'lang': 'zh_CN'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('errcode') == 0:
                return {
                    'nickname': data.get('nickname'),
                    'avatar': data.get('headimgurl'),
                    'openid': openid
                }
        except Exception as e:
            print(f"获取用户信息失败: {e}")
        
        return None
    
    def get_werun_data(self, openid, access_token):
        """获取微信运动数据（需要小程序环境）"""
        # 注意：这个API需要在小程序环境中调用
        url = "https://api.weixin.qq.com/wxa/business/getuserphonenumber"
        
        # 模拟返回数据结构
        return {
            'stepInfoList': [
                {
                    'timestamp': int(time.time()),
                    'step': 8888
                }
            ]
        }

class WeChatMiniProgram:
    """微信小程序相关功能"""
    
    @staticmethod
    def js_code_to_session(app_id, app_secret, js_code):
        """小程序登录凭证校验"""
        url = "https://api.weixin.qq.com/sns/jscode2session"
        params = {
            'appid': app_id,
            'secret': app_secret,
            'js_code': js_code,
            'grant_type': 'authorization_code'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            return response.json()
        except Exception as e:
            print(f"小程序登录失败: {e}")
            return {'errcode': -1, 'errmsg': str(e)}
    
    @staticmethod
    def decrypt_data(encrypted_data, iv, session_key):
        """解密微信数据"""
        import base64
        from Crypto.Cipher import AES
        
        try:
            session_key = base64.b64decode(session_key)
            encrypted_data = base64.b64decode(encrypted_data)
            iv = base64.b64decode(iv)
            
            cipher = AES.new(session_key, AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(encrypted_data)
            
            # 去除填充
            pad = decrypted[-1]
            decrypted = decrypted[:-pad]
            
            return json.loads(decrypted.decode('utf-8'))
        except Exception as e:
            print(f"解密数据失败: {e}")
            return None