import uuid
import time
import base64

class SimpleQRGenerator:
    def __init__(self):
        self.pending_binds = {}
    
    def generate_bind_qr(self, username):
        """生成简单的绑定二维码（文本形式）"""
        bind_code = str(uuid.uuid4())
        
        self.pending_binds[bind_code] = {
            'username': username,
            'created_at': time.time(),
            'status': 'pending'
        }
        
        # 生成简单的文本二维码
        qr_text = f"微信绑定码: {bind_code[:8]}"
        qr_svg = self.create_text_qr(qr_text)
        
        return {
            'bind_code': bind_code,
            'qr_image': f"data:image/svg+xml;base64,{base64.b64encode(qr_svg.encode()).decode()}",
            'expires_in': 300
        }
    
    def create_text_qr(self, text):
        """创建文本形式的二维码"""
        return f'''<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
            <rect width="200" height="200" fill="white" stroke="black" stroke-width="2"/>
            <text x="100" y="80" text-anchor="middle" font-family="Arial" font-size="12" fill="black">
                扫描绑定微信
            </text>
            <text x="100" y="110" text-anchor="middle" font-family="Arial" font-size="10" fill="black">
                {text}
            </text>
            <text x="100" y="140" text-anchor="middle" font-family="Arial" font-size="8" fill="gray">
                请使用微信扫一扫
            </text>
            <rect x="20" y="20" width="20" height="20" fill="black"/>
            <rect x="160" y="20" width="20" height="20" fill="black"/>
            <rect x="20" y="160" width="20" height="20" fill="black"/>
            <rect x="80" y="80" width="40" height="40" fill="black"/>
        </svg>'''
    
    def check_bind_status(self, bind_code):
        """检查绑定状态"""
        if bind_code not in self.pending_binds:
            return {'status': 'invalid'}
        
        bind_info = self.pending_binds[bind_code]
        
        if time.time() - bind_info['created_at'] > 300:
            del self.pending_binds[bind_code]
            return {'status': 'expired'}
        
        return {
            'status': bind_info['status'],
            'username': bind_info['username']
        }
    
    def confirm_bind(self, bind_code, openid, wechat_info):
        """确认绑定"""
        if bind_code not in self.pending_binds:
            return False
        
        bind_info = self.pending_binds[bind_code]
        bind_info['status'] = 'confirmed'
        bind_info['openid'] = openid
        bind_info['wechat_info'] = wechat_info
        
        return True