from api.app import app
from flask import send_from_directory
import os

# 添加静态文件路由，提供bgSound目录下的音频文件
@app.route('/bgSound/<path:filename>')
def bg_sound(filename):
    return send_from_directory(os.path.join(app.root_path, 'bgSound'), filename)

if __name__ == '__main__':
    print("好梦精灵启动中...")
    print("访问 http://localhost:5000 使用健康助手")
    app.run(host='0.0.0.0', port=5000, debug=True)