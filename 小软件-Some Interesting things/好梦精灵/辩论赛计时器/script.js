class DebateTimer {
    constructor() {
        this.currentPhaseIndex = 0;
        this.timeLeft = 0;
        this.totalTime = 0;
        this.isRunning = false;
        this.timer = null;
        this.audioContext = null;
        this.volume = 0.5;
        this.countdownInterval = null;
        
        this.defaultPhases = [
            { name: '正方一辩立论', duration: 300, warnings: [60, 30, 10] },
            { name: '反方一辩立论', duration: 300, warnings: [60, 30, 10] },
            { name: '正方二辩驳论', duration: 180, warnings: [30, 10] },
            { name: '反方二辩驳论', duration: 180, warnings: [30, 10] },
            { name: '正方三辩质辩', duration: 120, warnings: [30, 10] },
            { name: '反方三辩质辩', duration: 120, warnings: [30, 10] },
            { name: '自由辩论', duration: 600, warnings: [120, 60, 30, 10] },
            { name: '反方四辩总结', duration: 240, warnings: [60, 30, 10] },
            { name: '正方四辩总结', duration: 240, warnings: [60, 30, 10] }
        ];
        
        this.phases = [...this.defaultPhases];
        this.init();
    }

    init() {
        this.initAudio();
        this.bindEvents();
        this.loadSettings();
        this.loadTemplates();
        this.renderPhases();
        this.resetTimer();
    }

    initAudio() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (e) {
            console.warn('Audio context not supported');
        }
    }

    playBeep(frequency = 800, duration = 200) {
        if (!this.audioContext) return;
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.value = frequency;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(this.volume, this.audioContext.currentTime + 0.01);
        gainNode.gain.exponentialRampToValueAtTime(0.001, this.audioContext.currentTime + duration / 1000);
        
        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + duration / 1000);
    }

    bindEvents() {
        // 计时器控制
        document.getElementById('startBtn').addEventListener('click', () => {
            if (this.isRunning) {
                this.pause();
            } else {
                this.start();
            }
        });
        document.getElementById('pauseBtn').addEventListener('click', () => this.pause());
        document.getElementById('resetBtn').addEventListener('click', () => this.reset());
        document.getElementById('nextBtn').addEventListener('click', () => this.nextPhase());

        // 模态框控制
        document.getElementById('settingsBtn').addEventListener('click', () => this.openSettings());
        document.getElementById('templatesBtn').addEventListener('click', () => this.openTemplates());
        
        // 关闭模态框
        document.querySelectorAll('.close').forEach(close => {
            close.addEventListener('click', (e) => {
                e.target.closest('.modal').style.display = 'none';
            });
        });

        // 设置相关
        document.getElementById('saveSettingsBtn').addEventListener('click', () => this.saveSettings());
        document.getElementById('cancelSettingsBtn').addEventListener('click', () => this.closeSettings());
        document.getElementById('addPhaseBtn').addEventListener('click', () => this.addPhaseConfig());
        document.getElementById('volumeSlider').addEventListener('input', (e) => {
            this.volume = e.target.value / 100;
            document.getElementById('volumeValue').textContent = e.target.value + '%';
        });

        // 预览音效
        document.getElementById('previewSoundBtn').addEventListener('click', () => {
            this.playBeep(800, 300);
        });

        // 模板相关
        document.getElementById('saveTemplateBtn').addEventListener('click', () => this.saveTemplate());

        // 队徽上传
        document.getElementById('leftLogoInput').addEventListener('change', (e) => this.handleLogoUpload(e, 'left'));
        document.getElementById('rightLogoInput').addEventListener('change', (e) => this.handleLogoUpload(e, 'right'));

        // 背景和文字颜色
        document.getElementById('bgColor').addEventListener('change', (e) => this.updateBackgroundColor(e.target.value));
        document.getElementById('textColor').addEventListener('change', (e) => this.updateTextColor(e.target.value));
    }

    start() {
        if (this.timeLeft <= 0) return;
        if (this.isRunning) return;
        
        this.isRunning = true;
        this.updateButtonStates();
        this.timer = setInterval(() => {
            this.timeLeft--;
            this.updateDisplay();
            this.checkWarnings();
            this.showCountdown();
            
            if (this.timeLeft <= 0) {
                this.pause();
                this.playFinishSound();
                this.showFinishEffect();
                setTimeout(() => this.nextPhase(), 1500);
            }
        }, 1000);
    }

    pause() {
        this.isRunning = false;
        this.stopCountdownSound();
        this.updateButtonStates();
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    }

    reset() {
        this.pause();
        this.currentPhaseIndex = 0;
        this.resetTimer();
    }

    nextPhase() {
        this.pause();
        this.currentPhaseIndex++;
        if (this.currentPhaseIndex >= this.phases.length) {
            this.currentPhaseIndex = this.phases.length - 1;
            document.getElementById('currentPhase').textContent = '比赛结束';
            return;
        }
        this.resetTimer();
    }

    resetTimer() {
        this.stopCountdownSound();
        if (this.currentPhaseIndex < this.phases.length) {
            const currentPhase = this.phases[this.currentPhaseIndex];
            this.timeLeft = currentPhase.duration;
            this.totalTime = currentPhase.duration;
            document.getElementById('currentPhase').textContent = currentPhase.name;
        }
        document.getElementById('countdownOverlay').style.display = 'none';
        this.updateDisplay();
        this.updatePhasesList();
        this.updateButtonStates();
    }

    updateButtonStates() {
        const startBtn = document.getElementById('startBtn');
        if (this.isRunning) {
            startBtn.textContent = '暂停';
            startBtn.style.background = '#f39c12';
        } else {
            startBtn.textContent = '开始';
            startBtn.style.background = '#27ae60';
        }
    }

    updateDisplay() {
        const minutes = Math.floor(this.timeLeft / 60);
        const seconds = this.timeLeft % 60;
        const display = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        const timerDisplay = document.getElementById('timerDisplay');
        timerDisplay.textContent = display;
        
        // 更新进度条
        const progress = ((this.totalTime - this.timeLeft) / this.totalTime) * 100;
        document.getElementById('progress').style.width = `${progress}%`;
        
        // 更新警告状态
        timerDisplay.className = '';
        if (this.timeLeft <= 10) {
            timerDisplay.classList.add('timer-danger');
        } else if (this.timeLeft <= 30) {
            timerDisplay.classList.add('timer-warning');
        }
    }

    checkWarnings() {
        const currentPhase = this.phases[this.currentPhaseIndex];
        if (currentPhase && currentPhase.warnings.includes(this.timeLeft)) {
            if (this.timeLeft <= 10) {
                this.playBeep(1200, 300);
            } else if (this.timeLeft <= 30) {
                this.playBeep(900, 200);
            } else {
                this.playBeep(600, 150);
            }
        }
    }

    showCountdown() {
        const overlay = document.getElementById('countdownOverlay');
        const number = document.getElementById('countdownNumber');
        
        if (this.timeLeft <= 10 && this.timeLeft > 0) {
            overlay.style.display = 'flex';
            number.textContent = this.timeLeft;
            number.style.animation = 'none';
            setTimeout(() => {
                number.style.animation = 'countdownBounce 1s ease-in-out';
            }, 10);
            
            // 五秒倒计时开始播放长提示音
            if (this.timeLeft === 5) {
                this.startCountdownSound();
            }
        } else {
            overlay.style.display = 'none';
            this.stopCountdownSound();
        }
    }

    startCountdownSound() {
        this.stopCountdownSound();
        this.countdownInterval = setInterval(() => {
            this.playBeep(1200, 100);
        }, 200);
    }
    
    stopCountdownSound() {
        if (this.countdownInterval) {
            clearInterval(this.countdownInterval);
            this.countdownInterval = null;
        }
    }

    playFinishSound() {
        this.stopCountdownSound();
        // 结束时的特殊提示音：三声递增的哔声
        setTimeout(() => this.playBeep(800, 200), 0);
        setTimeout(() => this.playBeep(1000, 200), 300);
        setTimeout(() => this.playBeep(1200, 400), 600);
    }

    showFinishEffect() {
        const timerSection = document.querySelector('.timer-section');
        timerSection.classList.add('timer-finished');
        setTimeout(() => {
            timerSection.classList.remove('timer-finished');
        }, 1500);
    }

    updatePhasesList() {
        const phasesList = document.getElementById('phasesList');
        phasesList.innerHTML = '';
        
        this.phases.forEach((phase, index) => {
            const phaseItem = document.createElement('div');
            phaseItem.className = 'phase-item';
            phaseItem.textContent = `${phase.name} (${Math.floor(phase.duration / 60)}:${(phase.duration % 60).toString().padStart(2, '0')})`;
            
            if (index === this.currentPhaseIndex) {
                phaseItem.classList.add('active');
            } else if (index < this.currentPhaseIndex) {
                phaseItem.classList.add('completed');
            }
            
            phasesList.appendChild(phaseItem);
        });
    }

    renderPhases() {
        this.updatePhasesList();
    }

    openSettings() {
        document.getElementById('settingsModal').style.display = 'block';
        this.renderPhasesConfig();
    }

    closeSettings() {
        document.getElementById('settingsModal').style.display = 'none';
    }

    renderPhasesConfig() {
        const container = document.getElementById('phasesConfig');
        container.innerHTML = '';
        
        this.phases.forEach((phase, index) => {
            const phaseDiv = document.createElement('div');
            phaseDiv.className = 'phase-config';
            phaseDiv.innerHTML = `
                <input type="text" value="${phase.name}" placeholder="阶段名称" data-index="${index}" data-field="name">
                <input type="number" value="${phase.duration}" placeholder="时长(秒)" data-index="${index}" data-field="duration">
                <input type="text" value="${phase.warnings.join(',')}" placeholder="提醒时间点(秒,用逗号分隔)" data-index="${index}" data-field="warnings">
                <button onclick="debateTimer.removePhase(${index})">删除</button>
            `;
            container.appendChild(phaseDiv);
        });
    }

    addPhaseConfig() {
        this.phases.push({
            name: '新阶段',
            duration: 180,
            warnings: [30, 10]
        });
        this.renderPhasesConfig();
    }

    removePhase(index) {
        this.phases.splice(index, 1);
        this.renderPhasesConfig();
    }

    saveSettings() {
        // 保存阶段配置
        const configs = document.querySelectorAll('.phase-config input');
        configs.forEach(input => {
            const index = parseInt(input.dataset.index);
            const field = input.dataset.field;
            
            if (field === 'warnings') {
                this.phases[index][field] = input.value.split(',').map(w => parseInt(w.trim())).filter(w => !isNaN(w));
            } else if (field === 'duration') {
                this.phases[index][field] = parseInt(input.value) || 180;
            } else {
                this.phases[index][field] = input.value;
            }
        });
        
        // 保存其他设置
        const settings = {
            phases: this.phases,
            bgColor: document.getElementById('bgColor').value,
            textColor: document.getElementById('textColor').value,
            volume: this.volume,
            leftTeamName: document.getElementById('leftTeamName').textContent,
            rightTeamName: document.getElementById('rightTeamName').textContent
        };
        
        localStorage.setItem('debateTimerSettings', JSON.stringify(settings));
        
        this.reset();
        this.renderPhases();
        this.closeSettings();
    }

    loadSettings() {
        const saved = localStorage.getItem('debateTimerSettings');
        if (saved) {
            const settings = JSON.parse(saved);
            this.phases = settings.phases || this.defaultPhases;
            this.volume = settings.volume || 0.5;
            
            if (settings.bgColor) {
                document.getElementById('bgColor').value = settings.bgColor;
                this.updateBackgroundColor(settings.bgColor);
            }
            
            if (settings.textColor) {
                document.getElementById('textColor').value = settings.textColor;
                this.updateTextColor(settings.textColor);
            }
            
            if (settings.leftTeamName) {
                document.getElementById('leftTeamName').textContent = settings.leftTeamName;
            }
            
            if (settings.rightTeamName) {
                document.getElementById('rightTeamName').textContent = settings.rightTeamName;
            }
            
            document.getElementById('volumeSlider').value = this.volume * 100;
            document.getElementById('volumeValue').textContent = Math.round(this.volume * 100) + '%';
        }
    }

    updateBackgroundColor(color) {
        document.body.style.background = `linear-gradient(135deg, ${color}, ${this.adjustBrightness(color, -20)})`;
    }

    updateTextColor(color) {
        document.body.style.color = color;
    }

    adjustBrightness(hex, percent) {
        const num = parseInt(hex.replace("#", ""), 16);
        const amt = Math.round(2.55 * percent);
        const R = (num >> 16) + amt;
        const G = (num >> 8 & 0x00FF) + amt;
        const B = (num & 0x0000FF) + amt;
        return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
            (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
            (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1);
    }

    handleLogoUpload(event, side) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const img = document.getElementById(`${side}Logo`);
                const uploadBtn = document.querySelector(`#${side}LogoInput + .upload-btn`);
                const resetBtn = document.querySelector(`#${side}LogoInput + .upload-btn + .reset-logo-btn`);
                
                img.src = e.target.result;
                img.style.display = 'block';
                uploadBtn.style.display = 'none';
                resetBtn.style.display = 'block';
                
                // 保存到localStorage
                localStorage.setItem(`${side}TeamLogo`, e.target.result);
            };
            reader.readAsDataURL(file);
        }
    }

    resetLogo(side) {
        const img = document.getElementById(`${side}Logo`);
        const uploadBtn = document.querySelector(`#${side}LogoInput + .upload-btn`);
        const resetBtn = document.querySelector(`#${side}LogoInput + .upload-btn + .reset-logo-btn`);
        const input = document.getElementById(`${side}LogoInput`);
        
        img.src = '';
        img.style.display = 'none';
        uploadBtn.style.display = 'block';
        resetBtn.style.display = 'none';
        input.value = '';
        
        // 从localStorage删除
        localStorage.removeItem(`${side}TeamLogo`);
    }

    openTemplates() {
        document.getElementById('templatesModal').style.display = 'block';
        this.renderTemplates();
    }

    saveTemplate() {
        const name = document.getElementById('templateName').value.trim();
        if (!name) {
            alert('请输入模板名称');
            return;
        }
        
        const template = {
            name: name,
            phases: [...this.phases],
            leftTeamName: document.getElementById('leftTeamName').textContent,
            rightTeamName: document.getElementById('rightTeamName').textContent,
            bgColor: document.getElementById('bgColor').value,
            textColor: document.getElementById('textColor').value
        };
        
        const templates = this.getTemplates();
        templates[name] = template;
        localStorage.setItem('debateTimerTemplates', JSON.stringify(templates));
        
        document.getElementById('templateName').value = '';
        this.renderTemplates();
    }

    loadTemplate(name) {
        const templates = this.getTemplates();
        const template = templates[name];
        
        if (template) {
            this.phases = [...template.phases];
            document.getElementById('leftTeamName').textContent = template.leftTeamName;
            document.getElementById('rightTeamName').textContent = template.rightTeamName;
            
            if (template.bgColor) {
                document.getElementById('bgColor').value = template.bgColor;
                this.updateBackgroundColor(template.bgColor);
            }
            
            if (template.textColor) {
                document.getElementById('textColor').value = template.textColor;
                this.updateTextColor(template.textColor);
            }
            
            this.reset();
            this.renderPhases();
            document.getElementById('templatesModal').style.display = 'none';
        }
    }

    deleteTemplate(name) {
        const templates = this.getTemplates();
        delete templates[name];
        localStorage.setItem('debateTimerTemplates', JSON.stringify(templates));
        this.renderTemplates();
    }

    getTemplates() {
        const saved = localStorage.getItem('debateTimerTemplates');
        return saved ? JSON.parse(saved) : {};
    }

    renderTemplates() {
        const container = document.getElementById('templatesList');
        const templates = this.getTemplates();
        
        container.innerHTML = '';
        
        Object.keys(templates).forEach(name => {
            const templateDiv = document.createElement('div');
            templateDiv.className = 'template-item';
            templateDiv.innerHTML = `
                <span>${name}</span>
                <div class="template-actions">
                    <button onclick="debateTimer.loadTemplate('${name}')">加载</button>
                    <button onclick="debateTimer.deleteTemplate('${name}')" style="background: #e74c3c;">删除</button>
                </div>
            `;
            container.appendChild(templateDiv);
        });
    }

    loadTemplates() {
        // 加载保存的队徽
        const leftLogo = localStorage.getItem('leftTeamLogo');
        const rightLogo = localStorage.getItem('rightTeamLogo');
        
        if (leftLogo) {
            const img = document.getElementById('leftLogo');
            const uploadBtn = document.querySelector('#leftLogoInput + .upload-btn');
            const resetBtn = document.querySelector('#leftLogoInput + .upload-btn + .reset-logo-btn');
            img.src = leftLogo;
            img.style.display = 'block';
            uploadBtn.style.display = 'none';
            resetBtn.style.display = 'block';
        }
        
        if (rightLogo) {
            const img = document.getElementById('rightLogo');
            const uploadBtn = document.querySelector('#rightLogoInput + .upload-btn');
            const resetBtn = document.querySelector('#rightLogoInput + .upload-btn + .reset-logo-btn');
            img.src = rightLogo;
            img.style.display = 'block';
            uploadBtn.style.display = 'none';
            resetBtn.style.display = 'block';
        }
    }
}

// 初始化应用
let debateTimer;
window.addEventListener('DOMContentLoaded', () => {
    debateTimer = new DebateTimer();
});

// 键盘快捷键
document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT') return;
    
    switch(e.code) {
        case 'Space':
            e.preventDefault();
            if (debateTimer.isRunning) {
                debateTimer.pause();
            } else {
                debateTimer.start();
            }
            break;
        case 'KeyR':
            if (e.ctrlKey) {
                e.preventDefault();
                debateTimer.reset();
            }
            break;
        case 'KeyN':
            if (e.ctrlKey) {
                e.preventDefault();
                debateTimer.nextPhase();
            }
            break;
    }
});