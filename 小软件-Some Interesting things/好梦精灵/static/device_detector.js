class ClientDeviceDetector {
    static detectDevice() {
        const userAgent = navigator.userAgent.toLowerCase();
        const platform = navigator.platform.toLowerCase();
        
        return {
            isAndroid: /android/.test(userAgent),
            isIOS: /iphone|ipad|ipod/.test(userAgent),
            isWindows: /win/.test(platform),
            isMobile: /android|iphone|ipad|ipod|blackberry|iemobile|opera mini/.test(userAgent),
            userAgent: userAgent,
            platform: platform
        };
    }
    
    static async getAndroidData() {
        const device = this.detectDevice();
        
        if (device.isAndroid) {
            const batteryInfo = await this.getBatteryLevel();
            
            return {
                screen_time_hours: this.getScreenTime(),
                battery_level: batteryInfo.level,
                battery_charging: batteryInfo.charging,
                device_model: this.getDeviceModel(),
                android_version: this.getAndroidVersion(),
                steps: this.getStepCount(),
                memory_info: this.getMemoryInfo(),
                connection_info: this.getConnectionInfo(),
                data_source: 'android_browser'
            };
        }
        
        return null;
    }
    
    static getScreenTime() {
        const today = new Date().toDateString();
        let screenData = JSON.parse(localStorage.getItem('screenTime') || '{}');
        
        if (!screenData[today]) {
            screenData[today] = {
                startTime: Date.now(),
                totalTime: 0
            };
            localStorage.setItem('screenTime', JSON.stringify(screenData));
        }
        
        const currentSession = Date.now() - screenData[today].startTime;
        return Math.round(currentSession / (1000 * 3600) * 10) / 10;
    }
    
    static async getBatteryLevel() {
        try {
            if ('getBattery' in navigator) {
                const battery = await navigator.getBattery();
                const batteryInfo = {
                    level: Math.round(battery.level * 100),
                    charging: battery.charging,
                    chargingTime: battery.chargingTime,
                    dischargingTime: battery.dischargingTime
                };
                localStorage.setItem('batteryLevel', JSON.stringify(batteryInfo));
                return batteryInfo;
            }
        } catch (error) {
            console.log('电池API不可用:', error);
        }
        
        const saved = localStorage.getItem('batteryLevel');
        return saved ? JSON.parse(saved) : { level: null, charging: null };
    }
    
    static getDeviceModel() {
        const userAgent = navigator.userAgent;
        
        const patterns = [
            /Android.*?;\s*([^)]+)\)/,
            /\(([^;]+);.*Android/,
            /Android[^;]*;\s*([^)]+)/
        ];
        
        for (let pattern of patterns) {
            const match = userAgent.match(pattern);
            if (match && match[1]) {
                return match[1].trim();
            }
        }
        
        return 'Android Device';
    }
    
    static getAndroidVersion() {
        const userAgent = navigator.userAgent;
        const match = userAgent.match(/Android\s([0-9\.]+)/);
        return match ? match[1] : 'Unknown';
    }
    
    static getStepCount() {
        const today = new Date().toDateString();
        let stepsData = JSON.parse(localStorage.getItem('dailySteps') || '{}');
        return stepsData[today] || 0;
    }
    
    static updateSteps(steps) {
        const today = new Date().toDateString();
        let stepsData = JSON.parse(localStorage.getItem('dailySteps') || '{}');
        stepsData[today] = steps;
        localStorage.setItem('dailySteps', JSON.stringify(stepsData));
    }
    
    static getMemoryInfo() {
        if ('memory' in performance) {
            return {
                used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
                total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024),
                limit: Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024)
            };
        }
        return null;
    }
    
    static getConnectionInfo() {
        if ('connection' in navigator) {
            const conn = navigator.connection;
            return {
                type: conn.effectiveType,
                downlink: conn.downlink,
                rtt: conn.rtt,
                saveData: conn.saveData
            };
        }
        return null;
    }
    
    static async getSystemUptime() {
        try {
            // 尝试从服务器获取真实系统运行时间
            const response = await fetch('/api/system-uptime');
            if (response.ok) {
                const data = await response.json();
                return data.uptime_hours || 0;
            }
        } catch (error) {
            console.log('无法获取系统运行时间:', error);
        }
        
        // 备用方案：使用本地存储
        const startTime = localStorage.getItem('systemStartTime');
        if (!startTime) {
            localStorage.setItem('systemStartTime', Date.now().toString());
            return 0;
        }
        
        const uptime = Date.now() - parseInt(startTime);
        return Math.round(uptime / (1000 * 3600) * 10) / 10;
    }
    
    static initializeTracking() {
        // 初始化屏幕时间追踪
        const today = new Date().toDateString();
        let screenData = JSON.parse(localStorage.getItem('screenTime') || '{}');
        
        if (!screenData[today]) {
            screenData[today] = {
                startTime: Date.now(),
                totalTime: 0
            };
            localStorage.setItem('screenTime', JSON.stringify(screenData));
        }
        
        // 页面可见性变化追踪
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseScreenTracking();
            } else {
                this.resumeScreenTracking();
            }
        });
        
        // 定期更新屏幕时间
        setInterval(() => {
            this.updateScreenTime();
        }, 60000); // 每分钟更新
    }
    
    static updateScreenTime() {
        const today = new Date().toDateString();
        let screenData = JSON.parse(localStorage.getItem('screenTime') || '{}');
        
        if (screenData[today] && !document.hidden) {
            const currentTime = Date.now();
            const sessionTime = currentTime - screenData[today].startTime;
            screenData[today].totalTime = sessionTime;
            localStorage.setItem('screenTime', JSON.stringify(screenData));
        }
    }
    
    static pauseScreenTracking() {
        const today = new Date().toDateString();
        let screenData = JSON.parse(localStorage.getItem('screenTime') || '{}');
        
        if (screenData[today]) {
            screenData[today].pauseTime = Date.now();
            localStorage.setItem('screenTime', JSON.stringify(screenData));
        }
    }
    
    static resumeScreenTracking() {
        const today = new Date().toDateString();
        let screenData = JSON.parse(localStorage.getItem('screenTime') || '{}');
        
        if (screenData[today] && screenData[today].pauseTime) {
            const pauseDuration = Date.now() - screenData[today].pauseTime;
            screenData[today].startTime += pauseDuration;
            delete screenData[today].pauseTime;
            localStorage.setItem('screenTime', JSON.stringify(screenData));
        }
    }
}

function getIOSDevice() {
    const userAgent = navigator.userAgent;
    if (/iPhone/.test(userAgent)) {
        return 'iPhone';
    } else if (/iPad/.test(userAgent)) {
        return 'iPad';
    } else if (/iPod/.test(userAgent)) {
        return 'iPod';
    }
    return 'iOS Device';
}

// 初始化追踪
document.addEventListener('DOMContentLoaded', () => {
    ClientDeviceDetector.initializeTracking();
    createStars();
});

function createStars() {
    const starsContainer = document.createElement('div');
    starsContainer.className = 'stars';
    document.body.appendChild(starsContainer);
    
    for (let i = 0; i < 100; i++) {
        const star = document.createElement('div');
        star.className = 'star';
        star.style.left = Math.random() * 100 + '%';
        star.style.top = Math.random() * 100 + '%';
        star.style.animationDelay = Math.random() * 3 + 's';
        starsContainer.appendChild(star);
    }
}