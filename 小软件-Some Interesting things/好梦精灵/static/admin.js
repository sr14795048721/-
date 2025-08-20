document.addEventListener('DOMContentLoaded', function() {
    loadUsersList();
    loadSystemStats();
    
    document.getElementById('clear-data-btn').addEventListener('click', clearAllData);
    document.getElementById('reset-leaderboard-btn').addEventListener('click', resetLeaderboard);
    document.getElementById('export-data-btn').addEventListener('click', exportData);
});

async function loadUsersList() {
    try {
        const response = await fetch('/admin/users');
        const data = await response.json();
        
        let html = '<table class="users-table"><tr><th>用户名</th><th>状态</th><th>健康分数</th><th>IP地址</th><th>设备</th><th>微信</th><th>最后活动</th><th>操作</th></tr>';
        
        data.users.forEach(user => {
            const statusIcon = user.is_online ? '🟢' : '🔴';
            const statusText = user.is_online ? '在线' : '离线';
            const lastActive = user.last_active ? 
                new Date(user.last_active).toLocaleString('zh-CN') : '从未登录';
            const wechatStatus = user.wechat_openid ? 
                `🐈 ${user.wechat_nickname || '已绑定'}` : '未绑定';
            
            html += `
                <tr class="${user.is_online ? 'user-online' : 'user-offline'}">
                    <td>${user.username}</td>
                    <td><span class="status-indicator">${statusIcon} ${statusText}</span></td>
                    <td>${user.health_score}</td>
                    <td>${user.ip_address || 'N/A'}</td>
                    <td>${user.device_type}</td>
                    <td>${wechatStatus}</td>
                    <td><small>${lastActive}</small></td>
                    <td><button onclick="deleteUser('${user.username}')" class="btn-small btn-danger">删除</button></td>
                </tr>
            `;
        });
        
        html += '</table>';
        document.getElementById('users-list').innerHTML = html;
    } catch (error) {
        document.getElementById('users-list').innerHTML = '<p>加载用户列表失败</p>';
    }
}

async function loadSystemStats() {
    try {
        const response = await fetch('/admin/stats');
        const data = await response.json();
        
        // 计算在线用户数
        const usersResponse = await fetch('/admin/users');
        const usersData = await usersResponse.json();
        const onlineCount = usersData.users.filter(user => user.is_online).length;
        
        document.getElementById('total-users').textContent = data.total_users;
        document.getElementById('online-users').textContent = onlineCount;
        document.getElementById('active-users').textContent = data.active_users;
        document.getElementById('avg-score').textContent = data.avg_score.toFixed(1);
        
        // 统计微信绑定用户
        const wechatUsers = usersData.users.filter(user => user.wechat_openid).length;
        const bindRate = data.total_users > 0 ? ((wechatUsers / data.total_users) * 100).toFixed(1) : 0;
        
        document.getElementById('wechat-users').textContent = wechatUsers;
        document.getElementById('bind-rate').textContent = bindRate + '%';
    } catch (error) {
        console.error('加载统计数据失败:', error);
    }
}

async function clearAllData() {
    if (!confirm('确定要清除所有用户数据吗？此操作不可恢复！')) {
        return;
    }
    
    try {
        const response = await fetch('/admin/clear-data', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('数据清除成功');
            loadUsersList();
            loadSystemStats();
        } else {
            alert('数据清除失败: ' + result.message);
        }
    } catch (error) {
        alert('操作失败');
    }
}

async function deleteUser(username) {
    if (!confirm(`确定要删除用户 ${username} 吗？`)) {
        return;
    }
    
    try {
        const response = await fetch(`/admin/delete-user/${username}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('用户删除成功');
            loadUsersList();
            loadSystemStats();
        } else {
            alert('删除失败: ' + result.message);
        }
    } catch (error) {
        alert('删除失败');
    }
}

async function exportData() {
    try {
        const response = await fetch('/admin/export');
        const data = await response.json();
        
        const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `users_data_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
        
        document.getElementById('export-result').innerHTML = '<p style="color: green;">数据导出成功</p>';
    } catch (error) {
        document.getElementById('export-result').innerHTML = '<p style="color: red;">导出失败</p>';
    }
}

async function resetLeaderboard() {
    if (!confirm('确定要重置排行榜吗？所有用户的健康分数将清零！')) {
        return;
    }
    
    try {
        const response = await fetch('/admin/reset-leaderboard', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('排行榜重置成功');
            loadUsersList();
            loadSystemStats();
        } else {
            alert('重置失败: ' + result.message);
        }
    } catch (error) {
        alert('重置失败');
    }
}