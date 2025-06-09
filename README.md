# 🚀 Hệ Thống Truyền File An Toàn

Một ứng dụng web truyền file real-time với kiểm tra tính toàn vẹn SHA-256, được xây dựng bằng Python Flask và Socket.IO.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![Socket.IO](https://img.shields.io/badge/Socket.IO-5.3+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Tính Năng Chính

### 🔐 Bảo Mật
- **Kiểm tra tính toàn vẹn SHA-256**: Đảm bảo file không bị thay đổi trong quá trình truyền
- **Hệ thống xác thực**: Đăng nhập/đăng ký an toàn
- **Phân quyền Admin**: Quản lý toàn hệ thống

### 📡 Truyền File Real-time
- **Socket.IO**: Truyền file và thông báo real-time
- **Upload/Download**: Giao diện drag-and-drop thân thiện
- **Gửi cho người offline**: Hỗ trợ gửi file cho người dùng không online

### 👥 Quản Lý Người Dùng
- **Hiển thị trạng thái online**: Theo dõi người dùng đang hoạt động
- **Chọn người nhận**: Gửi file có mục tiêu cụ thể
- **Lịch sử cá nhân**: Theo dõi hoạt động của từng user

### 📊 Quản Trị Hệ Thống
- **Trang Admin**: Xem lịch sử tất cả người dùng
- **Thống kê**: Theo dõi hoạt động hệ thống
- **Lọc và tìm kiếm**: Quản lý dữ liệu hiệu quả

### 💾 Lưu Trữ
- **Database JSON**: Không cần SQL, dễ triển khai
- **Metadata file**: Lưu trữ thông tin chi tiết
- **Backup tự động**: Đảm bảo an toàn dữ liệu

## 🏗️ Cấu Trúc Dự Án
![Giao diện demo](/CayThuMuc.png)

## 🚀 Cài Đặt và Chạy

### Yêu Cầu Hệ Thống
- Python 3.8+
- Trình duyệt web hiện đại
- 100MB dung lượng trống

## 📋 Hướng Dẫn Sử Dụng

### 🔑 Đăng Ký và Đăng Nhập

1. Truy cập trang đăng ký
2. Tạo tài khoản mới (tài khoản đầu tiên sẽ tự động là Admin)
3. Đăng nhập với thông tin vừa tạo
![Giao diện demo](/DangNhap.png)
![Giao diện demo](/DangKy.png)


### 📤 Gửi File

1. Chọn file từ máy tính
2. Chọn người nhận từ danh sách
3. Nhấn "Gửi file"
4. Hệ thống sẽ tính toán mã băm SHA-256 và gửi


### 📥 Nhận File

1. File sẽ hiển thị trong bảng "File đã nhận"
2. Nhấn "Tải xuống" để download
3. Nhấn "Kiểm tra" để xác minh tính toàn vẹn


### 🔍 Kiểm Tra Tính Toàn Vẹn

1. Nhấn nút "Kiểm tra" bên cạnh file
2. Hệ thống sẽ hiển thị:

1. Mã băm gốc (khi gửi)
2. Mã băm hiện tại (kiểm tra)
3. Kết quả so sánh





### 👑 Tính Năng Admin

- Xem lịch sử tất cả người dùng
- Thống kê hoạt động hệ thống
- Lọc dữ liệu theo người dùng
- Quản lý toàn bộ file trong hệ thống


## 🛠️ Công Nghệ Sử Dụng

### Backend

- **Flask**: Web framework Python
- **Flask-SocketIO**: Real-time communication
- **Werkzeug**: File handling và security
- **Hashlib**: SHA-256 hashing


### Frontend

- **HTML5**: Semantic markup
- **CSS3**: Responsive design với Flexbox/Grid
- **JavaScript ES6+**: Modern client-side scripting
- **Socket.IO Client**: Real-time updates


### Database

- **JSON Files**: Lightweight data storage
- **File System**: Secure file storage


## 🔒 Bảo Mật

### Mã Hóa

- **SHA-256**: Kiểm tra tính toàn vẹn file
- **Password Hashing**: Mật khẩu được hash trước khi lưu
- **Session Management**: Quản lý phiên đăng nhập an toàn


### Validation

- **File Type Checking**: Kiểm tra loại file upload
- **Input Sanitization**: Làm sạch dữ liệu đầu vào
- **Access Control**: Phân quyền truy cập file


### Best Practices

- **Secure File Names**: Tên file được làm sạch
- **Path Traversal Protection**: Bảo vệ khỏi tấn công đường dẫn
- **CORS Configuration**: Cấu hình CORS an toàn


## 📱 Responsive Design

Ứng dụng được thiết kế responsive, hoạt động tốt trên:

- 🖥️ Desktop (1200px+)
- 💻 Laptop (768px - 1199px)
- 📱 Tablet (480px - 767px)
- 📱 Mobile (< 480px)


## 🎨 Giao Diện

### Màu Sắc Chính

- **Primary**: `#667eea` (Gradient blue)
- **Secondary**: `#764ba2` (Gradient purple)
- **Success**: `#48bb78` (Green)
- **Warning**: `#ed8936` (Orange)
- **Error**: `#f56565` (Red)


### Typography

- **Font Family**: Segoe UI, Tahoma, Geneva, Verdana, sans-serif
- **Responsive Sizing**: Tự động điều chỉnh theo màn hình

## 📊 API Endpoints

### Authentication

- `POST /login` - Đăng nhập
- `POST /register` - Đăng ký
- `GET /logout` - Đăng xuất


### File Operations

- `POST /upload` - Upload file
- `GET /download/<file_id>` - Download file
- `POST /api/verify_hash` - Kiểm tra mã băm


### Data APIs

- `GET /api/users` - Danh sách người dùng
- `GET /api/received-files` - File đã nhận
- `GET /api/history` - Lịch sử truyền file


