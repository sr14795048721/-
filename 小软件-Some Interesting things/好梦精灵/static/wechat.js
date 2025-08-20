// 微信相关功能
class WeChatIntegration {
    static isWeChatBrowser() {
        return /micromessenger/i.test(navigator.userAgent);
    }
    
    static async bindWeChat() {
        if (!currentUser) {
            alert('请先登录');
            return;
        }
        
        try {
            // 生成二维码
            const response = await fetch('/wechat/qr-bind', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: currentUser})
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showQRModal(result.qr_code, result.bind_code);
            } else {
                alert('生成二维码失败');
            }
        } catch (error) {
            alert('网络错误，请重试');
        }
    }
    
    static showQRModal(qrCode, bindCode) {
        // 创建二维码模态框
        const modal = document.createElement('div');
        modal.className = 'qr-modal';
        modal.innerHTML = `
            <div class="qr-modal-content">
                <div class="qr-header">
                    <h3>💚 微信绑定</h3>
                    <button class="qr-close">&times;</button>
                </div>
                <div class="qr-body">
                    <img src="${qrCode}" alt="二维码" class="qr-image">
                    <p>📱 请使用微信扫一扫上方二维码</p>
                    <p><small>🎭 模拟演示：点击下方按钮模拟扫码成功</small></p>
                    <button class="mock-scan-btn" onclick="WeChatIntegration.mockScanSuccess('${bindCode}')">✨ 模拟扫码成功</button>
                    <div class="qr-status">⏳ 等待扫码...</div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // 绑定关闭事件
        modal.querySelector('.qr-close').onclick = () => {
            document.body.removeChild(modal);
        };
        
        // 点击模态框外部关闭
        modal.onclick = (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        };
        
        // 开始轮询绑定状态
        this.pollBindStatus(bindCode, modal);
    }
    
    static async pollBindStatus(bindCode, modal) {
        const maxAttempts = 60; // 5分钟
        let attempts = 0;
        
        const poll = async () => {
            if (attempts >= maxAttempts) {
                modal.querySelector('.qr-status').textContent = '二维码已过期';
                return;
            }
            
            try {
                const response = await fetch(`/wechat/check-bind/${bindCode}`);
                const result = await response.json();
                
                if (result.status === 'confirmed') {
                    modal.querySelector('.qr-status').textContent = '✅ 绑定成功！';
                    setTimeout(() => {
                        document.body.removeChild(modal);
                        location.reload();
                    }, 1000);
                    return;
                } else if (result.status === 'expired') {
                    modal.querySelector('.qr-status').textContent = '⏰ 二维码已过期';
                    return;
                }
                
                attempts++;
                setTimeout(poll, 3000); // 3秒轮询一次
            } catch (error) {
                attempts++;
                setTimeout(poll, 3000);
            }
        };
        
        poll();
    }
    
    static async mockScanSuccess(bindCode) {
        // 模拟扫码成功
        try {
            const mockWeChatData = {
                openid: 'mock_openid_' + Date.now(),
                nickname: '微信用户' + Math.floor(Math.random() * 1000),
                avatar: 'https://via.placeholder.com/64x64/07c160/ffffff?text=微信'
            };
            
            // 直接绑定
            const response = await fetch('/wechat/bind', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    username: currentUser,
                    openid: mockWeChatData.openid,
                    wechat_info: mockWeChatData
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // 关闭模态框
                const modal = document.querySelector('.qr-modal');
                if (modal) {
                    document.body.removeChild(modal);
                }
                
                // 更新界面显示绑定状态
                WeChatIntegration.updateWeChatStatus(true, mockWeChatData);
                WeChatIntegration.loadWeChatSteps();
                
                // 显示成功消息
                const successMsg = document.createElement('div');
                successMsg.className = 'success-toast';
                successMsg.innerHTML = '🎉 <span class="toast-text">微信绑定成功！</span>';
                document.body.appendChild(successMsg);
                
                setTimeout(() => {
                    document.body.removeChild(successMsg);
                }, 3000);
            }
        } catch (error) {
            alert('绑定失败');
        }
    }
    
    static updateWeChatStatus(bound, wechatInfo = null) {
        const statusDiv = document.getElementById('wechat-status');
        const bindBtn = document.getElementById('bind-wechat-btn');
        
        if (bound && wechatInfo) {
            statusDiv.innerHTML = `
                <div class="wechat-bound">
                    <img src="${wechatInfo.avatar}" alt="头像" class="wechat-avatar">
                    <span>✅ 已绑定: ${wechatInfo.nickname}</span>
                    <button onclick="WeChatIntegration.loadWeChatSteps()" class="btn-small wechat-steps-btn">📊 获取步数</button>
                </div>
            `;
            if (bindBtn) bindBtn.style.display = 'none';
        } else {
            statusDiv.innerHTML = '<p class="wechat-unbound">❌ 未绑定微信</p>';
            if (bindBtn) bindBtn.style.display = 'inline-block';
        }
    }
    
    static async loadWeChatSteps() {
        if (!currentUser) return;
        
        try {
            const response = await fetch(`/wechat/steps/${currentUser}`);
            const result = await response.json();
            
            if (result.success) {
                const stepsData = result.data;
                this.displayWeChatSteps(stepsData);
            } else {
                console.log('获取微信步数失败:', result.message);
            }
        } catch (error) {
            console.log('获取微信步数失败:', error);
        }
    }
    
    static displayWeChatSteps(stepsData) {
        const statusDiv = document.getElementById('wechat-status');
        const existingSteps = statusDiv.querySelector('.wechat-steps');
        
        if (existingSteps) {
            existingSteps.remove();
        }
        
        const stepsDiv = document.createElement('div');
        stepsDiv.className = 'wechat-steps';
        stepsDiv.innerHTML = `
            <h4>🏃‍♂️ 微信运动数据</h4>
            <div class="steps-info">
                <div class="step-item">
                    <span class="step-label">📅 今日步数:</span>
                    <span class="step-value">${stepsData.today_steps.toLocaleString()}</span>
                </div>
                <div class="step-item">
                    <span class="step-label">📆 昨日步数:</span>
                    <span class="step-value">${stepsData.yesterday_steps.toLocaleString()}</span>
                </div>
            </div>
            <div class="week-steps">
                <h5>📈 本周步数趋势:</h5>
                <div class="steps-chart">
                    ${stepsData.week_steps.map((steps, index) => `
                        <div class="step-bar">
                            <div class="bar" style="height: ${(steps / 10000) * 100}%"></div>
                            <span class="day">周${index + 1}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        statusDiv.appendChild(stepsDiv);
        
        // 更新本地步数记录
        ClientDeviceDetector.updateSteps(stepsData.today_steps);
    }
    
    static initWeChatFeatures() {
        // 检查是否在微信环境
        if (this.isWeChatBrowser()) {
            document.body.classList.add('wechat-browser');
        }
        
        // 绑定事件
        const bindBtn = document.getElementById('bind-wechat-btn');
        if (bindBtn) {
            bindBtn.addEventListener('click', () => this.bindWeChat());
        }
    }
}

// 页面加载完成后初始化微信功能
document.addEventListener('DOMContentLoaded', () => {
    WeChatIntegration.initWeChatFeatures();
});