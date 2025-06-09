from flask import Flask, render_template, request, jsonify, session, send_file, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import hashlib
import os
import uuid
from datetime import datetime
import base64
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
socketio = SocketIO(app, cors_allowed_origins="*")

# Tạo thư mục cần thiết
os.makedirs('data', exist_ok=True)
os.makedirs('static/uploads', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# Khởi tạo file JSON
def init_json_files():
    files_to_init = {
        'data/users.json': {},
        'data/history.json': [],
        'data/files.json': {}
    }
    
    for file_path, default_content in files_to_init.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_content, f, ensure_ascii=False, indent=2)

init_json_files()

# Utility functions
def load_json(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {} if 'users' in filename or 'files' in filename else []

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# Biến lưu trữ users online
online_users = {}

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        users = load_json('data/users.json')
        
        if username in users and users[username]['password'] == hashlib.sha256(password.encode()).hexdigest():
            session['username'] = username
            session['is_admin'] = users[username].get('is_admin', False)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Tên đăng nhập hoặc mật khẩu không đúng'})
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        users = load_json('data/users.json')
        
        if username in users:
            return jsonify({'success': False, 'message': 'Tên đăng nhập đã tồn tại'})
        
        # Tạo admin đầu tiên
        is_admin = len(users) == 0
        
        users[username] = {
            'password': hashlib.sha256(password.encode()).hexdigest(),
            'is_admin': is_admin,
            'created_at': datetime.now().isoformat()
        }
        
        save_json('data/users.json', users)
        return jsonify({'success': True})
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/history')
def history():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('history.html')

@app.route('/admin')
def admin():
    if 'username' not in session or not session.get('is_admin'):
        return redirect(url_for('index'))
    return render_template('admin.html')

@app.route('/api/users')
def get_users():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    users = load_json('data/users.json')
    user_list = []
    for username, user_data in users.items():
        if username != session['username']:  # Không hiển thị chính mình
            user_list.append({
                'username': username,
                'online': username in online_users
            })
    
    return jsonify(user_list), 200, {'Cache-Control': 'public, max-age=5'}

# Thêm API mới để lấy danh sách file đã nhận
@app.route('/api/received-files')
def get_received_files():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    files_data = load_json('data/files.json')
    received_files = []
    
    for file_id, file_info in files_data.items():
        if file_info['receiver'] == session['username']:
            received_files.append({
                'file_id': file_id,
                'filename': file_info['original_name'],
                'sender': file_info['sender'],
                'receiver': file_info['receiver'],
                'hash': file_info['hash'],
                'timestamp': file_info['timestamp']
            })
    
    # Sắp xếp theo thời gian mới nhất
    received_files.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return jsonify(received_files)

@app.route('/api/history')
def get_history():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    history = load_json('data/history.json')
    
    if session.get('is_admin'):
        # Admin có thể xem tất cả
        return jsonify(history)
    else:
        # User chỉ xem lịch sử của mình
        user_history = [h for h in history if h['sender'] == session['username'] or h['receiver'] == session['username']]
        return jsonify(user_history)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'Không có file'}), 400
    
    file = request.files['file']
    receiver = request.form.get('receiver')
    
    if file.filename == '':
        return jsonify({'error': 'Không có file được chọn'}), 400
    
    if not receiver:
        return jsonify({'error': 'Chưa chọn người nhận'}), 400
    
    # Kiểm tra người nhận có tồn tại không
    users = load_json('data/users.json')
    if receiver not in users:
        return jsonify({'error': 'Người nhận không tồn tại'}), 400
    
    # Lưu file
    filename = secure_filename(file.filename)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
    file.save(file_path)
    
    # Tính SHA-256
    file_hash = calculate_sha256(file_path)
    
    # Lưu metadata
    files_data = load_json('data/files.json')
    files_data[file_id] = {
        'original_name': filename,
        'file_path': file_path,
        'hash': file_hash,
        'sender': session['username'],
        'receiver': receiver,
        'timestamp': datetime.now().isoformat(),
        'is_read': False
    }
    save_json('data/files.json', files_data)
    
    # Lưu lịch sử
    history = load_json('data/history.json')
    history.append({
        'id': file_id,
        'filename': filename,
        'sender': session['username'],
        'receiver': receiver,
        'hash': file_hash,
        'timestamp': datetime.now().isoformat(),
        'status': 'sent'
    })
    save_json('data/history.json', history)
    
    # Gửi thông báo qua socket nếu người nhận đang online
    if receiver in online_users:
        socketio.emit('file_received', {
            'file_id': file_id,
            'filename': filename,
            'sender': session['username'],
            'hash': file_hash
        }, room=receiver)
    
    return jsonify({
        'success': True,
        'file_id': file_id,
        'hash': file_hash
    })

@app.route('/download/<file_id>')
def download_file(file_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    files_data = load_json('data/files.json')
    
    if file_id not in files_data:
        return "File không tồn tại", 404
    
    file_info = files_data[file_id]
    
    # Kiểm tra quyền download
    if session['username'] != file_info['receiver'] and session['username'] != file_info['sender'] and not session.get('is_admin'):
        return "Không có quyền truy cập", 403
    
    # Đánh dấu file đã đọc nếu người tải là người nhận
    if session['username'] == file_info['receiver'] and not file_info.get('is_read', False):
        file_info['is_read'] = True
        save_json('data/files.json', files_data)
    
    return send_file(file_info['file_path'], as_attachment=True, download_name=file_info['original_name'])

@app.route('/api/verify_hash', methods=['POST'])
def verify_hash():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    file_id = data.get('file_id')
    
    files_data = load_json('data/files.json')
    
    if file_id not in files_data:
        return jsonify({'error': 'File không tồn tại'}), 404
    
    file_info = files_data[file_id]
    
    # Tính lại hash
    current_hash = calculate_sha256(file_info['file_path'])
    original_hash = file_info['hash']
    
    is_valid = current_hash == original_hash
    
    return jsonify({
        'valid': is_valid,
        'original_hash': original_hash,
        'current_hash': current_hash
    })

# Socket events
@socketio.on('connect')
def on_connect():
    if 'username' in session:
        username = session['username']
        online_users[username] = request.sid
        join_room(username)
        
        # Thông báo user online
        socketio.emit('user_online', {
            'username': username,
            'online_users': list(online_users.keys())
        }, broadcast=True)
        
        # Gửi thông báo về các file chưa đọc
        files_data = load_json('data/files.json')
        unread_files = []
        
        for file_id, file_info in files_data.items():
            if file_info['receiver'] == username and not file_info.get('is_read', False):
                unread_files.append({
                    'file_id': file_id,
                    'filename': file_info['original_name'],
                    'sender': file_info['sender'],
                    'hash': file_info['hash'],
                    'timestamp': file_info['timestamp']
                })
                
                # Đánh dấu là đã đọc
                file_info['is_read'] = True
        
        if unread_files:
            save_json('data/files.json', files_data)
            
            for file in unread_files:
                socketio.emit('file_received', file, room=username)

@socketio.on('disconnect')
def on_disconnect():
    if 'username' in session:
        username = session['username']
        if username in online_users:
            leave_room(username)
            del online_users[username]
            
            # Thông báo user offline
            socketio.emit('user_offline', {
                'username': username,
                'online_users': list(online_users.keys())
            }, broadcast=True)

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 HỆ THỐNG TRUYỀN FILE AN TOÀN")
    print("=" * 60)
    print("📡 Server đang chạy tại:")
    print("🌐 http://localhost:5000")
    print("🔐 http://127.0.0.1:5000")
    print("=" * 60)
    print("📋 Hướng dẫn sử dụng:")
    print("1. Mở trình duyệt và truy cập link trên")
    print("2. Đăng ký tài khoản mới (tài khoản đầu tiên sẽ là Admin)")
    print("3. Đăng nhập và bắt đầu truyền file")
    print("=" * 60)
    print("⚡ Nhấn Ctrl+C để dừng server")
    print("=" * 60)
    
    try:
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("🛑 Server đã dừng. Cảm ơn bạn đã sử dụng!")
        print("=" * 60)
