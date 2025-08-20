import pygame
import os
import threading
import time

class MusicPlayer:
    def __init__(self):
        self.is_playing = False
        self.is_paused = False
        self.current_music = None
        self.volume = 0.3
        self.music_thread = None
        
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            print("音频系统初始化成功")
        except Exception as e:
            print(f"音频系统初始化失败: {e}")
            print("请确保已安装pygame: pip install pygame")
    
    def load_music(self, music_file):
        """加载音乐文件"""
        try:
            # 构建完整的音乐文件路径
            base_path = os.path.dirname(__file__)
            full_path = os.path.join(base_path, 'bgSound', music_file)
            if os.path.exists(full_path):
                pygame.mixer.music.load(full_path)
                self.current_music = full_path
                return True
            else:
                # 尝试其他可能的路径
                alternate_path = os.path.join(base_path, 'static', 'bgSound', music_file)
                if os.path.exists(alternate_path):
                    pygame.mixer.music.load(alternate_path)
                    self.current_music = alternate_path
                    print(f"在备用路径找到音乐文件: {alternate_path}")
                    return True
                else:
                    print(f"音乐文件不存在: {full_path}")
                    print(f"备用路径也不存在: {alternate_path}")
                    # 列出实际存在的文件
                    bg_sound_dir = os.path.join(base_path, 'bgSound')
                    if os.path.exists(bg_sound_dir):
                        files = os.listdir(bg_sound_dir)
                        print(f"bgSound目录中的文件: {files}")
                    return False
        except Exception as e:
            print(f"加载音乐失败: {e}")
            return False
    
    def play(self, loops=-1):
        """播放音乐"""
        try:
            if self.current_music:
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play(loops)
                self.is_playing = True
                self.is_paused = False
                print(f"正在播放音乐: {self.current_music}")
                return True
            else:
                print("未加载音乐文件")
        except Exception as e:
            print(f"播放音乐失败: {e}")
        return False
    
    def pause(self):
        """暂停音乐"""
        try:
            pygame.mixer.music.pause()
            self.is_paused = True
        except Exception as e:
            print(f"暂停音乐失败: {e}")
    
    def resume(self):
        """恢复播放"""
        try:
            pygame.mixer.music.unpause()
            self.is_paused = False
        except Exception as e:
            print(f"恢复播放失败: {e}")
    
    def stop(self):
        """停止音乐"""
        try:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.is_paused = False
        except Exception as e:
            print(f"停止音乐失败: {e}")
    
    def set_volume(self, volume):
        """设置音量 (0.0 - 1.0)"""
        try:
            self.volume = max(0.0, min(1.0, volume))
            pygame.mixer.music.set_volume(self.volume)
        except Exception as e:
            print(f"设置音量失败: {e}")
    
    def is_music_playing(self):
        """检查音乐是否正在播放"""
        try:
            return pygame.mixer.music.get_busy() and not self.is_paused
        except:
            return False
    
    def toggle_play_pause(self):
        """切换播放/暂停状态"""
        if self.is_music_playing():
            self.pause()
            return False
        elif self.is_paused:
            self.resume()
            return True
        else:
            return self.play()

# 全局音乐播放器实例
music_player = MusicPlayer()