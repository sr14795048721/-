let userPoints = 0;
let sleepData = [];
let currentUser = null;

document.addEventListener('DOMContentLoaded', function() {
    initAuth();
    document.getElementById('analyze_sleep').addEventListener('click', analyzeSleep);
    document.getElementById('analyze_behavior').addEventListener('click', analyzeBehavior);
    loadSystemInfo();
    loadSleepPattern();
    updateClock();
    setInterval(updateClock, 1000);
    setInterval(loadSystemInfo, 5000);
    setInterval(loadSleepPattern, 30000);
    loadLeaderboard();
    setInterval(loadLeaderboard, 60000);
    
    // 初始化背景音乐
    initBackgroundMusic();
});

function initBackgroundMusic() {
    const bgMusic = document.getElementById('bgMusic');
    const musicToggle = document.getElementById('musicToggle');
    const audioNotice = document.getElementById('audioNotice');
    let isPlaying = false;
    let userInteracted = false;
    
    bgMusic.volume = 0.3;
    
    // 显示音频提示
    setTimeout(() => {
        if (!userInteracted && audioNotice) {
            audioNotice.style.display = 'block';
        }
    }, 2000);
    
    musicToggle.addEventListener('click', (e) => {
        e.stopPropagation();
        userInteracted = true;
        hideAudioNotice();
        
        if (isPlaying) {
            bgMusic.pause();
            musicToggle.textContent = '🎵';
            musicToggle.classList.remove('playing');
            isPlaying = false;
        } else {
            bgMusic.play().then(() => {
                musicToggle.textContent = '🔇';
                musicToggle.classList.add('playing');
                isPlaying = true;
            }).catch(e => {
                console.error('音乐播放失败:', e);
                alert('🎵 音乐播放失败\n\n可能原因：\n1. 浏览器阻止了自动播放\n2. 音频文件加载失败\n3. 设备音量已静音\n\n请检查浏览器设置和设备音量');
            });
        }
    });
    
    // 用户交互后尝试播放
    const enableAudio = (e) => {
        if (!userInteracted && !isPlaying) {
            userInteracted = true;
            hideAudioNotice();
            
            bgMusic.play().then(() => {
                musicToggle.textContent = '🔇';
                musicToggle.classList.add('playing');
                isPlaying = true;
            }).catch(e => {
                console.log('需要用户手动启用音乐');
            });
        }
    };
    
    document.addEventListener('click', enableAudio);
    document.addEventListener('touchstart', enableAudio);
    document.addEventListener('keydown', enableAudio);
}

function hideAudioNotice() {
    const audioNotice = document.getElementById('audioNotice');
    if (audioNotice) {
        audioNotice.style.display = 'none';
    }
}

function showMusicError(message) {
    // 显示弹窗
    alert('🎵 音乐播放错误\n\n' + message + '\n\n请检查浏览器设置或尝试刷新页面');
    
    // 同时显示页面提示
    const errorDiv = document.createElement('div');
    errorDiv.className = 'music-error';
    errorDiv.innerHTML = `
        <div class="error-content">
            <span class="error-icon">⚠️</span>
            <span class="error-text">${message}</span>
            <button class="error-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
        </div>
    `;
    document.body.appendChild(errorDiv);
    
    // 5秒后自动消失
    setTimeout(() => {
        if (errorDiv.parentElement) {
            errorDiv.remove();
        }
    }, 5000);
}

function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleString('zh-CN');
    document.querySelector('#system-info-content p:last-child').textContent = `当前时间: ${timeString}`;
}

async function analyzeSleep() {
    const sleepHours = document.getElementById('sleep_hours').value;
    const bedtime = document.getElementById('bedtime').value;
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: 'user1',
                sleep_hours: parseFloat(sleepHours),
                bedtime: bedtime
            })
        });
        
        const result = await response.json();
        const healthLevel = result.health_level || {level: '一般', color: '#FFC107', icon: '⚠️'};
        
        document.getElementById('sleep_result').innerHTML = `
            <h3>📋 分析结果</h3>
            <div class="health-score-display">
                <span class="health-icon">${healthLevel.icon}</span>
                <span class="health-text" style="color: ${healthLevel.color}">${healthLevel.level}</span>
                <span class="score-text">${result.predicted_quality.toFixed(1)}/10</span>
            </div>
            <p><strong>⚡ 睡眠效率:</strong> ${result.sleep_efficiency || '正常'}</p>
            <p><strong>💡 建议:</strong> ${result.recommendation || '继续保持良好作息'}</p>
        `;
        
        // 更新健康分数显示（累计形式）
        if (result.total_health_score !== undefined) {
            document.getElementById('health_score').textContent = result.total_health_score.toFixed(1);
            document.getElementById('score_bar').style.width = `${Math.min((result.total_health_score / 100) * 100, 100)}%`;
            document.getElementById('score_bar').style.backgroundColor = healthLevel.color;
        }
        

    } catch (error) {
        document.getElementById('sleep_result').innerHTML = `
            <div class="error-message">
                <h3>⚠️ 睡眠分析失败</h3>
                <p>网络连接错误: ${error.message}</p>
                <p>请检查网络连接或稍后重试</p>
                <button onclick="analyzeSleep()" class="retry-btn">🔄 重试</button>
            </div>
        `;
    }
}

async function analyzeBehavior() {
    const exercise = parseInt(document.getElementById('exercise').value);
    
    try {
        const sysResponse = await fetch('/system-info');
        const sysData = await sysResponse.json();
        
        let score = 100;
        let suggestions = [];
        
        if (sysData.screen_time_hours > 4) {
            score -= 20;
            suggestions.push('减少屏幕使用时间');
        }
        if (exercise < 30) {
            score -= 15;
            suggestions.push('增加运动时间');
        }
        
        // 检测客户端设备
        const clientDevice = ClientDeviceDetector.detectDevice();
        let requestData = {
            user_id: currentUser,
            exercise: exercise
        };
        
        // 添加客户端数据
        if (clientDevice.isAndroid) {
            const androidData = ClientDeviceDetector.getAndroidData();
            requestData.client_data = androidData;
        } else {
            // 其他平台使用真实数据
            requestData.client_data = {
                screen_time_hours: ClientDeviceDetector.getScreenTime(),
                steps: ClientDeviceDetector.getStepCount(),
                data_source: clientDevice.isIOS ? 'ios_browser' : 
                           clientDevice.isWindows ? 'windows_browser' : 'browser'
            };
        }
        
        const response2 = await fetch('/analyze-behavior', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(requestData)
        });
        
        const behaviorResult = await response2.json();
        
        const healthLevel = behaviorResult.health_level || {level: '一般', color: '#FFC107', icon: '⚠️'};
        
        document.getElementById('behavior_result').innerHTML = `
            <h3>📊 行为分析结果</h3>
            <div class="data-source-info">
                <small>📡 数据来源: ${getDataSourceText(behaviorResult.data_source)}</small>
            </div>
            <div class="behavior-stats">
                <div class="stat-item">
                    <span class="stat-label">📱 屏幕使用:</span>
                    <span class="stat-value">${behaviorResult.screen_time}小时</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">🏃‍♂️ 运动时间:</span>
                    <span class="stat-value">${behaviorResult.exercise_time}分钟</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">👣 步数:</span>
                    <span class="stat-value">${behaviorResult.steps}步</span>
                </div>
            </div>
            <div class="health-score-display">
                <span class="health-icon">${healthLevel.icon}</span>
                <span class="health-text" style="color: ${healthLevel.color}">${healthLevel.level}</span>
                <span class="score-text">${behaviorResult.behavior_score}/10</span>
            </div>
        `;
        
        // 更新健康分数显示（累计形式）
        if (behaviorResult.total_health_score !== undefined) {
            document.getElementById('health_score').textContent = behaviorResult.total_health_score.toFixed(1);
            document.getElementById('score_bar').style.width = `${Math.min((behaviorResult.total_health_score / 100) * 100, 100)}%`;
            document.getElementById('score_bar').style.backgroundColor = healthLevel.color;
        }
        

    } catch (error) {
        document.getElementById('behavior_result').innerHTML = `
            <div class="error-message">
                <h3>⚠️ 行为分析失败</h3>
                <p>网络连接错误: ${error.message}</p>
                <p>请检查网络连接或稍后重试</p>
                <button onclick="analyzeBehavior()" class="retry-btn">🔄 重试</button>
            </div>
        `;
    }
}

function updatePoints(points) {
    userPoints += points;
    document.getElementById('points').textContent = userPoints;
    document.getElementById('points_bar').style.width = `${Math.min(userPoints, 100)}%`;
    
    if (userPoints >= 50) {
        addBadge('健康达人');
    }
}

function addBadge(badgeName) {
    const badgesContainer = document.getElementById('badges');
    if (!badgesContainer.querySelector(`[data-badge="${badgeName}"]`)) {
        const badge = document.createElement('div');
        badge.className = 'badge';
        badge.setAttribute('data-badge', badgeName);
        badge.textContent = `🏆 ${badgeName}`;
        badgesContainer.appendChild(badge);
    }
}

function updateChart(sleepHours) {
    sleepData.push(sleepHours);
    if (sleepData.length > 7) sleepData.shift();
    
    const ctx = document.getElementById('sleepChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: sleepData.map((_, i) => `第${i+1}天`),
            datasets: [{
                label: '睡眠时长',
                data: sleepData,
                borderColor: '#4CAF50',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {beginAtZero: true, max: 12}
            }
        }
    });
}

async function loadSystemInfo() {
    try {
        // 始终使用客户端检测的数据
        const clientDevice = ClientDeviceDetector.detectDevice();
        let data;
        
        if (clientDevice.isAndroid) {
            const androidData = await ClientDeviceDetector.getAndroidData();
            data = {
                os: 'Android',
                current_time: new Date().toLocaleString('zh-CN'),
                system_uptime_hours: await ClientDeviceDetector.getSystemUptime(),
                screen_time_hours: androidData.screen_time_hours,
                app_runtime_hours: 0.1,
                battery_level: androidData.battery_level,
                device_model: androidData.device_model,
                data_source: 'client_detected'
            };
        } else if (clientDevice.isIOS) {
            const batteryInfo = await ClientDeviceDetector.getBatteryLevel();
            data = {
                os: 'iOS',
                current_time: new Date().toLocaleString('zh-CN'),
                screen_time_hours: ClientDeviceDetector.getScreenTime(),
                app_runtime_hours: 0.1,
                battery_level: batteryInfo.level,
                device_model: getIOSDevice(),
                data_source: 'client_detected'
            };
        } else if (clientDevice.isWindows) {
            data = {
                os: 'Windows',
                current_time: new Date().toLocaleString('zh-CN'),
                screen_time_hours: ClientDeviceDetector.getScreenTime(),
                app_runtime_hours: 0.2,
                data_source: 'client_detected'
            };
        } else {
            data = {
                os: navigator.platform || 'Unknown',
                current_time: new Date().toLocaleString('zh-CN'),
                screen_time_hours: ClientDeviceDetector.getScreenTime(),
                app_runtime_hours: 0.1,
                data_source: 'client_detected'
            };
        }
        
        let systemHtml = `
            <p>🟢 系统状态: 正常运行</p>
            <p>💻 操作系统: ${data.os}</p>
            <p>🕐 当前时间: ${data.current_time}</p>
        `;
        
        if (currentUser) {
            systemHtml += `
                <p>📱 屏幕使用: ${data.screen_time_hours}小时</p>
                <p>⚡ 应用运行: ${data.app_runtime_hours}小时</p>
            `;
            
            // 只显示可靠的信息
            if (data.battery_level && data.battery_level > 0) {
                systemHtml += `<p>🔋 电池电量: ${data.battery_level}%</p>`;
            }
            if (data.device_model && data.device_model !== 'Unknown') {
                systemHtml += `<p>📲 设备型号: ${data.device_model}</p>`;
            }
        }
        
        document.getElementById('system-info-content').innerHTML = systemHtml;
    } catch (error) {
        document.getElementById('system-info-content').innerHTML = `
            <p>系统状态: 正常运行</p>
            <p>当前时间: ${new Date().toLocaleString('zh-CN')}</p>
        `;
    }
}

async function loadSleepPattern() {
    if (!currentUser) return;
    
    try {
        const response = await fetch('/sleep-pattern');
        const data = await response.json();
        
        let patternText = '';
        if (data.pattern.is_sleep_time) {
            patternText = '🌙 当前为睡眠时间';
            if (data.pattern.estimated_sleep_duration) {
                patternText += `，估算睡眠时长: ${data.pattern.estimated_sleep_duration}小时`;
            }
        } else {
            patternText = '☀️ 当前为清醒时间';
        }
        
        if (data.trends) {
            patternText += `<br>近期平均睡眠: ${data.trends.avg_sleep_hours}小时`;
        }
        
        document.getElementById('sleep_pattern').innerHTML = patternText;
    } catch (error) {
        document.getElementById('sleep_pattern').innerHTML = '睡眠模式检测中...';
    }
}

function initAuth() {
    const loginBtn = document.getElementById('login-btn');
    const registerBtn = document.getElementById('register-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const modal = document.getElementById('auth-modal');
    const closeBtn = document.querySelector('.close');
    
    loginBtn.onclick = () => showAuthModal('login');
    registerBtn.onclick = () => showAuthModal('register');
    logoutBtn.onclick = logout;
    closeBtn.onclick = () => modal.style.display = 'none';
}

function showAuthModal(type) {
    const modal = document.getElementById('auth-modal');
    const title = document.getElementById('modal-title');
    const submitBtn = document.getElementById('auth-submit');
    
    title.textContent = type === 'login' ? '登录' : '注册';
    submitBtn.textContent = type === 'login' ? '登录' : '注册';
    submitBtn.onclick = () => type === 'login' ? login() : register();
    
    modal.style.display = 'block';
}

async function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    const response = await fetch('/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, password})
    });
    
    const result = await response.json();
    if (result.success) {
        currentUser = result.user_id;
        updateUserDisplay();
        document.getElementById('auth-modal').style.display = 'none';
        
        // 更新用户会话
        await fetch('/update-session', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: currentUser})
        });
        
        // 检查是否为管理员
        if (currentUser === 'admin') {
            document.getElementById('admin-btn').style.display = 'inline';
        }
    } else {
        alert(result.message);
    }
}

async function register() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    const response = await fetch('/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, password})
    });
    
    const result = await response.json();
    alert(result.message);
    if (result.success) {
        document.getElementById('auth-modal').style.display = 'none';
    }
}

function logout() {
    currentUser = null;
    document.getElementById('admin-btn').style.display = 'none';
    updateUserDisplay();
}

function updateUserDisplay() {
    const userSpan = document.getElementById('current-user');
    const loginBtn = document.getElementById('login-btn');
    const registerBtn = document.getElementById('register-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const userContent = document.getElementById('user-content');
    const loginPrompt = document.getElementById('login-prompt');
    
    if (currentUser) {
        userSpan.textContent = `当前用户: ${currentUser}`;
        loginBtn.style.display = 'none';
        registerBtn.style.display = 'none';
        logoutBtn.style.display = 'inline';
        userContent.style.display = 'block';
        loginPrompt.style.display = 'none';
        loadUserData();
    } else {
        userSpan.textContent = '未登录';
        loginBtn.style.display = 'inline';
        registerBtn.style.display = 'inline';
        logoutBtn.style.display = 'none';
        userContent.style.display = 'none';
        loginPrompt.style.display = 'block';
        document.getElementById('health_score').textContent = '0';
        document.getElementById('score_bar').style.width = '0%';
    }
}

async function loadLeaderboard() {
    try {
        const response = await fetch('/leaderboard');
        const data = await response.json();
        
        // 过滤有分数的用户
        const filteredLeaderboard = data.leaderboard.filter(([name, score]) => score > 0);
        
        let html = '<div class="leaderboard-grid">';
        filteredLeaderboard.forEach(([name, score], index) => {
            const rank = index + 1;
            const rankIcon = rank === 1 ? '🏆' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : `✨${rank}`;
            const scoreColor = score >= 8 ? '#4CAF50' : score >= 6 ? '#FFC107' : '#FF5722';
            const healthLevel = score >= 8 ? '🌟 优秀' : score >= 6 ? '💫 良好' : '🌱 一般';
            
            html += `
                <div class="leaderboard-item rank-${rank}">
                    <div class="rank">${rankIcon}</div>
                    <div class="user-info">
                        <div class="username">${name}</div>
                    </div>
                    <div class="score">
                        <span class="score-value">${score.toFixed(1)}</span>
                    </div>
                </div>
            `;
        });
        
        if (filteredLeaderboard.length === 0) {
            html += '<div class="no-data">📊 暂无有效数据</div>';
        }
        
        html += '</div>';
        
        document.getElementById('leaderboard-content').innerHTML = html;
    } catch (error) {
        document.getElementById('leaderboard-content').innerHTML = '加载失败';
    }
}

async function loadChart(type) {
    if (!currentUser) {
        alert('请先登录');
        return;
    }
    
    try {
        let url;
        if (type === 'leaderboard') {
            url = '/charts/leaderboard';
        } else {
            url = `/charts/${type}/${currentUser}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        // 隐藏所有图表
        document.querySelectorAll('.chart-container img').forEach(img => {
            img.style.display = 'none';
        });
        
        // 显示对应图表
        const chartImg = document.getElementById(`${type}-chart`);
        if (data.chart) {
            chartImg.src = data.chart;
            chartImg.style.display = 'block';
        }
    } catch (error) {
        alert('加载图表失败');
    }
}

function getDataSourceText(dataSource) {
    switch(dataSource) {
        case 'android_native':
            return 'Android系统';
        case 'android_adb':
            return 'Android设备';
        case 'client_detected':
            return '客户端检测';
        case 'wechat_sports':
            return '微信运动';
        default:
            return '系统检测';
    }
}

async function loadUserData() {
    if (!currentUser) return;
    
    try {
        const response = await fetch(`/user/${currentUser}`);
        const userData = await response.json();
        
        const healthScore = userData.health_score || 0;
        document.getElementById('health_score').textContent = healthScore;
        document.getElementById('score_bar').style.width = `${(healthScore / 10) * 100}%`;
    } catch (error) {
        console.error('加载用户数据失败:', error);
    }
}