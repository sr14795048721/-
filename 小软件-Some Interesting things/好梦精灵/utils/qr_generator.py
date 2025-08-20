import qrcode
import io
import base64
import uuid
import time
import json

class QRCodeGenerator:
    def __init__(self):
        self.pending_binds = {}  # 存储待绑定的二维码
    
    def generate_bind_qr(self, username):
        """生成微信绑定二维码"""
        # 生成唯一的绑定码
        bind_code = str(uuid.uuid4())
        
        # 存储绑定信息
        self.pending_binds[bind_code] = {
            'username': username,
            'created_at': time.time(),
            'status': 'pending'
        }
        
        # 生成二维码内容（实际应用中这里是微信小程序码）
        qr_content = f"https://your-domain.com/wechat/bind?code={bind_code}"
        
        # 创建二维码
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_content)
        qr.make(fit=True)
        
        # 生成图片
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 转换为base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            'bind_code': bind_code,
            'qr_image': f"data:image/png;base64,{img_str}",
            'expires_in': 300  # 5分钟过期
        }
    
    def check_bind_status(self, bind_code):
        """检查绑定状态"""
        if bind_code not in self.pending_binds:
            return {'status': 'invalid'}
        
        bind_info = self.pending_binds[bind_code]
        
        # 检查是否过期
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
    
    def cleanup_expired(self):
        """清理过期的绑定码"""
        current_time = time.time()
        expired_codes = [
            code for code, info in self.pending_binds.items()
            if current_time - info['created_at'] > 300
        ]
        
        for code in expired_codes:
            del self.pending_binds[code]