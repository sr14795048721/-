import sys
import os

# Add the parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from flask import Flask, request, jsonify, render_template, send_from_directory  # 导入Flask框架及相关模块
from services.sleep_service import SleepService
from services.user_service import UserService
from utils.sleep_tracker import SleepTracker
from utils.android_system import CrossPlatformSystem
from utils.chart_generator import ChartGenerator
from utils.user_tracker import UserTracker
import platform  # 导入睡眠服务业务逻辑
from services.behavior_service import BehaviorService  # 导入行为分析服务
from services.incentive_service import IncentiveService  # 导入激励服务
from services.chat_service import ChatService  # 导入聊天服务
from utils.error_reporter import error_reporter, auto_report_error
from utils.error_reporter import report_generator
from utils.scheduler import auto_scheduler

# 可选导入数据可视化工具
try:
    from utils.data_visualization import DataVisualizer
    data_visualizer = DataVisualizer()
    VISUALIZATION_AVAILABLE = True
except ImportError:
    data_visualizer = None
    VISUALIZATION_AVAILABLE = False

app = Flask(__name__, 
            template_folder=os.path.join(parent_dir, 'static'),
            static_folder=os.path.join(parent_dir, 'static'))  # 创建Flask应用实例
sleep_service = SleepService()
sleep_tracker = SleepTracker()
user_service = UserService()
chart_generator = ChartGenerator()
user_tracker = UserTracker()
behavior_service = BehaviorService()  # 实例化行为分析服务
incentive_service = IncentiveService()  # 实例化激励服务
chat_service = ChatService()  # 实例化聊天服务

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat_room():
    return render_template('chat.html')

@app.route('/static/bgSound/<filename>')
def serve_audio(filename):
    return send_from_directory('bgSound', filename)

@app.route('/analyze', methods=['POST'])
def analyze_sleep():
    data = request.json
    
    # 使用新的睡眠分析器
    analysis = sleep_tracker.analyze_sleep_quality(
        data['sleep_hours'],
        data['bedtime']
    )
    
    result = {
        'user_id': data['user_id'],
        'sleep_hours': data['sleep_hours'],
        'bedtime': data['bedtime'],
        'predicted_quality': analysis['quality_score'],
        'recommendation': '; '.join(analysis['suggestions']) if analysis['suggestions'] else '睡眠质量良好',
        'sleep_efficiency': analysis['sleep_efficiency']
    }
    
    # 累加用户健康分数
    total_score = user_service.add_health_score(data['user_id'], analysis['quality_score'])
    result['total_health_score'] = total_score
    
    return jsonify(result)

@app.route('/analyze-behavior', methods=['POST'])
def analyze_behavior():
    data = request.json
    
    # 检查是否有客户端数据（Android浏览器）
    if 'client_data' in data and data['client_data']:
        client_data = data['client_data']
        # 使用客户端数据
        screen_time = client_data.get('screen_time_hours', 2.5)
        steps = client_data.get('steps', 5000)
        exercise_time = data.get('exercise', 30)
        
        from utils.health_calculator import HealthCalculator
        behavior_score = HealthCalculator.calculate_behavior_score(screen_time, exercise_time)
        health_level = HealthCalculator.get_health_level(behavior_score)
        
        result = {
            'score': behavior_score,
            'screen_time': screen_time,
            'exercise_time': exercise_time,
            'steps': steps,
            'health_level': health_level,
            'data_source': 'android_browser',
            'behavior_score': behavior_score
        }
    else:
        # 使用服务器端数据
        sys_info = CrossPlatformSystem.get_system_info()
        data['screen_time_hours'] = sys_info.get('screen_time_hours', 0)
        
        result = behavior_service.analyze_behavior(data)
        behavior_score = result.get('score', 0)
        result['behavior_score'] = behavior_score
    
    # 累加用户健康分数
    total_score = user_service.add_health_score(data['user_id'], result['behavior_score'])
    result['total_health_score'] = total_score
    
    return jsonify(result)

@app.route('/user/<user_id>/points', methods=['GET'])
def get_user_points(user_id):
    """获取用户积分"""
    points = incentive_service.get_user_points(user_id)
    return jsonify({'points': points})

@app.route('/user/<user_id>/badges', methods=['GET'])
def get_user_badges(user_id):
    """获取用户徽章"""
    badges = incentive_service.get_user_badges(user_id)
    return jsonify({'badges': badges})

@app.route('/user/<user_id>/habits', methods=['GET', 'POST'])
def user_habits(user_id):
    """获取或更新用户习惯"""
    if request.method == 'GET':
        habits = incentive_service.get_user_habits(user_id)
        return jsonify({'habits': habits})
    else:
        data = request.json
        habit_name = data.get('habit_name')
        progress = data.get('progress')
        updated_habits = incentive_service.update_habit(user_id, habit_name, progress)
        return jsonify({'habits': updated_habits})

@app.route('/visualize/sleep', methods=['POST'])
def visualize_sleep():
    """生成睡眠数据可视化图表"""
    if not VISUALIZATION_AVAILABLE:
        return jsonify({'error': '可视化功能不可用'}), 501
    
    data = request.json
    sleep_data = data.get('sleep_data', [])
    chart_img = data_visualizer.create_sleep_chart(sleep_data)
    if chart_img:
        return jsonify({'chart': chart_img})
    else:
        return jsonify({'error': '无法生成图表'}), 500

@app.route('/visualize/behavior', methods=['POST'])
def visualize_behavior():
    """生成行为数据可视化图表"""
    if not VISUALIZATION_AVAILABLE:
        return jsonify({'error': '可视化功能不可用'}), 501
    
    data = request.json
    behavior_data = data.get('behavior_data', [])
    chart_img = data_visualizer.create_behavior_chart(behavior_data)
    if chart_img:
        return jsonify({'chart': chart_img})
    else:
        return jsonify({'error': '无法生成图表'}), 500

@app.route('/system-info', methods=['GET'])
def get_system_info():
    """获取系统信息"""
    return jsonify(CrossPlatformSystem.get_system_info())

@app.route('/sleep-pattern', methods=['GET'])
def get_sleep_pattern():
    """获取睡眠模式检测"""
    pattern = sleep_tracker.detect_sleep_pattern()
    trends = sleep_tracker.get_sleep_trends()
    return jsonify({
        'pattern': pattern,
        'trends': trends
    })

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    result = user_service.register_user(data['username'], data['password'])
    return jsonify(result)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    result = user_service.login_user(data['username'], data['password'])
    return jsonify(result)

@app.route('/user/<username>', methods=['GET'])
def get_user(username):
    user_info = user_service.get_user_info(username)
    if user_info:
        return jsonify(user_info)
    return jsonify({'error': '用户不存在'}), 404

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    leaderboard = user_service.get_leaderboard()
    return jsonify({'leaderboard': leaderboard})

@app.route('/charts/sleep/<username>', methods=['GET'])
def get_sleep_chart(username):
    user_info = user_service.get_user_info(username)
    if user_info and user_info.get('sleep_data'):
        chart = chart_generator.create_sleep_chart(user_info['sleep_data'])
        return jsonify({'chart': chart})
    return jsonify({'error': '无数据'}), 404

@app.route('/charts/leaderboard', methods=['GET'])
def get_leaderboard_chart():
    leaderboard = user_service.get_leaderboard()
    chart = chart_generator.create_leaderboard_chart(leaderboard)
    return jsonify({'chart': chart})

@app.route('/charts/behavior/<username>', methods=['GET'])
def get_behavior_chart(username):
    user_info = user_service.get_user_info(username)
    if user_info:
        behavior_data = {
            'screen_time': 4,  # 示例数据
            'exercise': 30,
            'sleep_quality': user_info.get('health_score', 70)
        }
        chart = chart_generator.create_behavior_chart(behavior_data)
        return jsonify({'chart': chart})
    return jsonify({'error': '用户不存在'}), 404

@app.route('/admin')
def admin_panel():
    return render_template('admin.html')

@app.route('/step-counter')
def step_counter():
    return render_template('step_counter.html')

@app.route('/admin/users', methods=['GET'])
def get_all_users():
    users_data = []
    user_status = user_tracker.get_all_user_status()
    
    for username, data in user_service.users.items():
        if not data.get('is_admin', False):
            status = user_status.get(username, {})
            users_data.append({
                'username': username,
                'health_score': data.get('health_score', 0),
                'created_at': data.get('created_at', ''),
                'is_online': status.get('is_online', False),
                'last_active': status.get('last_active'),
                'ip_address': status.get('ip_address'),
                'device_type': status.get('device_type', 'Unknown'),
                'wechat_openid': data.get('wechat_openid'),
                'wechat_nickname': data.get('wechat_info', {}).get('nickname')
            })
    return jsonify({'users': users_data})

@app.route('/admin/stats', methods=['GET'])
def get_system_stats():
    regular_users = [data for data in user_service.users.values() if not data.get('is_admin', False)]
    total_users = len(regular_users)
    active_users = len([u for u in regular_users if u.get('health_score', 0) > 0])
    avg_score = sum(u.get('health_score', 0) for u in regular_users) / max(total_users, 1)
    
    return jsonify({
        'total_users': total_users,
        'active_users': active_users,
        'avg_score': avg_score
    })

@app.route('/admin/clear-data', methods=['POST'])
def clear_all_data():
    # 清除所有非管理员用户数据
    for username, data in user_service.users.items():
        if not data.get('is_admin', False):
            data['health_score'] = 0
            data['sleep_data'] = {}
            data['behavior_data'] = {}
    
    user_service.save_users()
    return jsonify({'success': True, 'message': '数据清除成功'})

@app.route('/admin/reset-leaderboard', methods=['POST'])
def reset_leaderboard():
    user_service.reset_all_scores()
    return jsonify({'success': True, 'message': '排行榜重置成功'})

@app.route('/api/system-uptime', methods=['GET'])
def get_system_uptime():
    try:
        from utils.system_api import SystemAPI
        uptime = SystemAPI.get_system_uptime()
        memory_info = None
        
        system = platform.system().lower()
        if system == 'windows':
            memory_info = SystemAPI.get_windows_memory_info()
        elif system == 'linux':
            memory_info = SystemAPI.get_android_memory_info()
        
        return jsonify({
            'uptime_hours': uptime,
            'memory_info': memory_info,
            'system': system
        })
    except Exception:
        return jsonify({
            'uptime_hours': 0,
            'memory_info': None,
            'system': platform.system().lower()
        })

@app.route('/wechat/login', methods=['POST'])
def wechat_login():
    from utils.wechat_api import WeChatMiniProgram
    
    data = request.json
    js_code = data.get('code')
    
    if not js_code:
        return jsonify({'success': False, 'message': '缺少登录凭证'})
    
    # 获取微信用户信息
    result = WeChatMiniProgram.js_code_to_session(
        user_service.wechat_app_id,
        user_service.wechat_app_secret,
        js_code
    )
    
    if result.get('errcode'):
        return jsonify({'success': False, 'message': '微信登录失败'})
    
    openid = result.get('openid')
    session_key = result.get('session_key')
    
    return jsonify({
        'success': True,
        'openid': openid,
        'session_key': session_key
    })

@app.route('/wechat/bind', methods=['POST'])
def bind_wechat():
    data = request.json
    username = data.get('username')
    openid = data.get('openid')
    wechat_info = data.get('wechat_info', {})
    
    if not username or not openid:
        return jsonify({'success': False, 'message': '参数不完整'})
    
    success = user_service.bind_wechat(username, openid, wechat_info)
    
    if success:
        return jsonify({'success': True, 'message': '微信绑定成功'})
    else:
        return jsonify({'success': False, 'message': '用户不存在'})

@app.route('/wechat/qr-bind', methods=['POST'])
def generate_wechat_qr():
    from utils.simple_qr import SimpleQRGenerator
    
    data = request.json
    username = data.get('username')
    
    if not username:
        return jsonify({'success': False, 'message': '缺少用户名'})
    
    qr_generator = SimpleQRGenerator()
    qr_data = qr_generator.generate_bind_qr(username)
    
    return jsonify({
        'success': True,
        'qr_code': qr_data['qr_image'],
        'bind_code': qr_data['bind_code'],
        'expires_in': qr_data['expires_in']
    })

@app.route('/wechat/check-bind/<bind_code>', methods=['GET'])
def check_bind_status(bind_code):
    from utils.simple_qr import SimpleQRGenerator
    
    qr_generator = SimpleQRGenerator()
    status = qr_generator.check_bind_status(bind_code)
    
    if status['status'] == 'confirmed':
        bind_info = qr_generator.pending_binds[bind_code]
        user_service.bind_wechat(
            status['username'],
            bind_info['openid'],
            bind_info['wechat_info']
        )
    
    return jsonify(status)

@app.route('/wechat/steps/<username>', methods=['GET'])
def get_wechat_steps(username):
    user_info = user_service.get_user_info(username)
    if not user_info or not user_info.get('wechat_openid'):
        return jsonify({'success': False, 'message': '未绑定微信'})
    
    # 模拟返回微信运动数据
    steps_data = {
        'today_steps': 8888,
        'yesterday_steps': 7777,
        'week_steps': [6000, 7000, 8000, 9000, 8500, 7500, 8888]
    }
    
    return jsonify({
        'success': True,
        'data': steps_data
    })

@app.route('/admin/delete-user/<username>', methods=['DELETE', 'POST'])
def delete_user(username):
    if username in user_service.users and not user_service.users[username].get('is_admin', False):
        del user_service.users[username]
        user_service.save_users()
        return jsonify({'success': True, 'message': '用户删除成功'})
    return jsonify({'success': False, 'message': '用户不存在或无权限删除'})

@app.route('/update-session', methods=['POST'])
def update_session():
    data = request.json
    username = data.get('username')
    if username:
        user_tracker.update_user_session(username)
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/admin/user-status', methods=['GET'])
def get_user_status():
    all_status = user_tracker.get_all_user_status()
    return jsonify({'user_status': all_status})

@app.route('/admin/export', methods=['GET'])
def export_users_data():
    export_data = {}
    for username, data in user_service.users.items():
        if not data.get('is_admin', False):
            export_data[username] = {
                'health_score': data.get('health_score', 0),
                'created_at': data.get('created_at', ''),
                'sleep_data': data.get('sleep_data', {}),
                'behavior_data': data.get('behavior_data', {})
            }
    return jsonify(export_data)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

# 聊天室相关路由
@app.route('/chat/send', methods=['POST'])
def send_message():
    data = request.json
    username = data.get('username')
    message = data.get('message')
    
    if not username or not message:
        return jsonify({'success': False, 'message': '参数不完整'})
    
    msg = chat_service.add_message(username, message)
    return jsonify({'success': True, 'message': msg})

@app.route('/chat/messages', methods=['GET'])
def get_messages():
    messages = chat_service.get_recent_messages()
    return jsonify({'messages': messages})

@app.route('/chat/join', methods=['POST'])
def join_chat():
    data = request.json
    username = data.get('username')
    
    if username:
        chat_service.join_room(username)
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/chat/leave', methods=['POST'])
def leave_chat():
    data = request.json
    username = data.get('username')
    
    if username:
        chat_service.leave_room(username)
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/chat/online', methods=['GET'])
def get_online_users():
    count = chat_service.get_online_count()
    users = chat_service.get_online_users()
    return jsonify({'count': count, 'users': users})

@app.route('/error-report', methods=['GET'])  # 错误报告接口
def get_error_report():
    """获取错误报告摘要"""
    try:
        days = request.args.get('days', 7, type=int)
        report_file = report_generator.generate_summary_report(days)
        analysis = report_generator.analyze_errors(days)
        return jsonify({
            'status': 'success',
            'report_file': report_file,
            'summary': analysis
        })
    except Exception as e:
        error_reporter.capture_error(e, {'endpoint': '/error-report'})
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/auto-report/start', methods=['POST'])  # 启动自动报告
def start_auto_report():
    """启动自动报告生成"""
    try:
        auto_scheduler.start()
        return jsonify({'status': 'success', 'message': '自动报告已启动'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/auto-report/stop', methods=['POST'])  # 停止自动报告
def stop_auto_report():
    """停止自动报告生成"""
    try:
        auto_scheduler.stop()
        return jsonify({'status': 'success', 'message': '自动报告已停止'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 全局错误处理器
@app.errorhandler(Exception)
def handle_exception(e):
    """全局异常处理器"""
    error_reporter.capture_error(e, {
        'request_url': request.url,
        'request_method': request.method,
        'request_data': str(request.get_json()) if request.is_json else None
    })
    return jsonify({'error': '服务器内部错误', 'message': str(e)}), 500

if __name__ == '__main__':  # 主程序入口
    auto_scheduler.start()  # 启动自动报告调度器
    app.run(debug=True)     # 启动Flask开发服务器，开启调试模式