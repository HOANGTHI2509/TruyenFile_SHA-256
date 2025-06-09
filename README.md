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
