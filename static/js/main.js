// Kết nối Socket.IO
const socket = io()

// Biến global
const currentUser = ""
let onlineUsers = []
let receivedFiles = []

// Khởi tạo khi trang load
document.addEventListener("DOMContentLoaded", () => {
  loadUsers()
  loadReceivedFiles()
  setupEventListeners()
})

// Thiết lập event listeners
function setupEventListeners() {
  // Form upload file
  document.getElementById("uploadForm").addEventListener("submit", handleFileUpload)

  // Socket events
  socket.on("connect", () => {
    console.log("Đã kết nối socket")
  })

  socket.on("user_online", (data) => {
    updateOnlineUsers(data.online_users)
  })

  socket.on("user_offline", (data) => {
    updateOnlineUsers(data.online_users)
  })

  socket.on("file_received", (data) => {
    addReceivedFile(data)
    addNotification(`Bạn đã nhận file "${data.filename}" từ ${data.sender}`)
  })
}

// Tải danh sách users
async function loadUsers() {
  try {
    const response = await fetch("/api/users")
    const users = await response.json()

    const select = document.getElementById("receiverSelect")
    select.innerHTML = '<option value="">Chọn người nhận</option>'

    users.forEach((user) => {
      const option = document.createElement("option")
      option.value = user.username
      option.textContent = user.username + (user.online ? " (Online)" : " (Offline)")
      select.appendChild(option)
    })

    // Cập nhật danh sách người dùng online
    const onlineUsersList = document.getElementById("onlineUsersList")
    onlineUsersList.innerHTML = ""

    const onlineUsersArray = users.filter((u) => u.online).map((u) => u.username)
    onlineUsers = onlineUsersArray

    onlineUsersArray.forEach((username) => {
      const li = document.createElement("li")
      li.innerHTML = `
        <span class="online-indicator"></span>
        ${username}
      `
      onlineUsersList.appendChild(li)
    })
  } catch (error) {
    console.error("Lỗi khi tải danh sách users:", error)
  }
}

// Tải danh sách file đã nhận
async function loadReceivedFiles() {
  try {
    const response = await fetch("/api/received-files")
    const files = await response.json()

    receivedFiles = files
    displayReceivedFiles(files)
  } catch (error) {
    console.error("Lỗi khi tải danh sách file đã nhận:", error)
  }
}

// Hiển thị danh sách file đã nhận
function displayReceivedFiles(files) {
  const tbody = document.getElementById("receivedFilesTableBody")
  const noFilesMessage = document.getElementById("noFilesMessage")

  tbody.innerHTML = ""

  if (files.length === 0) {
    noFilesMessage.style.display = "block"
    return
  }

  noFilesMessage.style.display = "none"

  files.forEach((file) => {
    const row = document.createElement("tr")
    row.innerHTML = `
      <td>${formatDate(file.timestamp)}</td>
      <td>${file.filename}</td>
      <td>${file.sender}</td>
      <td>${file.receiver}</td>
      <td class="hash-cell" title="${file.hash}">${file.hash.substring(0, 16)}...</td>
      <td class="action-buttons">
        <a href="/download/${file.file_id}" class="btn-download">Tải xuống</a>
        <button onclick="verifyFileHashModal('${file.file_id}')" class="btn-verify">Kiểm tra</button>
      </td>
    `
    tbody.appendChild(row)
  })
}

// Thêm file mới vào danh sách đã nhận
function addReceivedFile(data) {
  const newFile = {
    file_id: data.file_id,
    filename: data.filename,
    sender: data.sender,
    receiver: getCurrentUsername(),
    hash: data.hash,
    timestamp: new Date().toISOString(),
  }

  receivedFiles.unshift(newFile)
  displayReceivedFiles(receivedFiles)
}

// Lấy username hiện tại (có thể lấy từ session hoặc API)
function getCurrentUsername() {
  // Tạm thời return "current_user", có thể cải thiện sau
  return "current_user"
}

// Cập nhật danh sách users online
function updateOnlineUsers(users) {
  onlineUsers = users
  const list = document.getElementById("onlineUsersList")
  list.innerHTML = ""

  users.forEach((username) => {
    const li = document.createElement("li")
    li.innerHTML = `
      <span class="online-indicator"></span>
      ${username}
    `
    list.appendChild(li)
  })

  updateSelectBoxStatus(users)
}

// Hàm mới để cập nhật trạng thái online trong select box
function updateSelectBoxStatus(onlineUsers) {
  const select = document.getElementById("receiverSelect")
  if (!select) return

  Array.from(select.options).forEach((option) => {
    if (option.value && option.value !== "") {
      const isOnline = onlineUsers.includes(option.value)
      const username = option.value
      option.textContent = username + (isOnline ? " (Online)" : " (Offline)")
    }
  })
}

// Xử lý upload file
async function handleFileUpload(e) {
  e.preventDefault()

  const fileInput = document.getElementById("fileInput")
  const receiverSelect = document.getElementById("receiverSelect")

  if (!fileInput.files[0]) {
    alert("Vui lòng chọn file")
    return
  }

  if (!receiverSelect.value) {
    alert("Vui lòng chọn người nhận")
    return
  }

  const formData = new FormData()
  formData.append("file", fileInput.files[0])
  formData.append("receiver", receiverSelect.value)

  try {
    const submitBtn = e.target.querySelector('button[type="submit"]')
    const originalText = submitBtn.textContent
    submitBtn.textContent = "Đang gửi..."
    submitBtn.disabled = true

    const response = await fetch("/upload", {
      method: "POST",
      body: formData,
    })

    const result = await response.json()

    if (result.success) {
      const isReceiverOnline = onlineUsers.includes(receiverSelect.value)

      addNotification(`Đã gửi file "${fileInput.files[0].name}" cho ${receiverSelect.value}`)

      if (!isReceiverOnline) {
        addNotification(
          `⚠️ Lưu ý: ${receiverSelect.value} hiện đang offline. Họ sẽ nhận được file khi đăng nhập lại.`,
          "warning",
        )
      }

      addNotification(`Mã băm SHA-256: ${result.hash}`)

      fileInput.value = ""
      receiverSelect.value = ""
    } else {
      alert("Lỗi: " + result.error)
    }

    submitBtn.textContent = originalText
    submitBtn.disabled = false
  } catch (error) {
    console.error("Lỗi khi upload:", error)
    alert("Có lỗi xảy ra khi gửi file")

    const submitBtn = e.target.querySelector('button[type="submit"]')
    submitBtn.textContent = "Gửi file"
    submitBtn.disabled = false
  }
}

// Thêm thông báo
function addNotification(message, type = "") {
  const container = document.getElementById("notificationsList")

  const notificationDiv = document.createElement("div")
  notificationDiv.className = type ? `notification ${type}` : "notification"
  notificationDiv.innerHTML = `
        <p>${message}</p>
        <small>${new Date().toLocaleString("vi-VN")}</small>
    `

  container.insertBefore(notificationDiv, container.firstChild)

  const notifications = container.querySelectorAll(".notification")
  if (notifications.length > 10) {
    notifications[notifications.length - 1].remove()
  }
}

// Kiểm tra mã băm file với modal
async function verifyFileHashModal(fileId) {
  try {
    const response = await fetch("/api/verify_hash", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ file_id: fileId }),
    })

    const result = await response.json()

    // Hiển thị modal với thông tin chi tiết
    document.getElementById("originalHash").textContent = result.original_hash
    document.getElementById("currentHash").textContent = result.current_hash

    const resultDiv = document.getElementById("hashResult")
    if (result.valid) {
      resultDiv.innerHTML = `
        <div class="hash-match">
          <span class="status-icon">✅</span>
          <span class="status-text">Mã băm trùng khớp - File nguyên vẹn</span>
        </div>
      `
      resultDiv.className = "hash-result success"
    } else {
      resultDiv.innerHTML = `
        <div class="hash-mismatch">
          <span class="status-icon">❌</span>
          <span class="status-text">Mã băm không khớp - File có thể đã bị thay đổi</span>
        </div>
      `
      resultDiv.className = "hash-result error"
    }

    document.getElementById("hashModal").style.display = "block"
  } catch (error) {
    console.error("Lỗi khi kiểm tra mã băm:", error)
    alert("Có lỗi xảy ra khi kiểm tra mã băm.")
  }
}

// Đóng modal
function closeHashModal() {
  document.getElementById("hashModal").style.display = "none"
}

// Đóng modal khi click bên ngoài
window.onclick = (event) => {
  const modal = document.getElementById("hashModal")
  if (event.target === modal) {
    modal.style.display = "none"
  }
}

// Utility functions
function formatDate(dateString) {
  return new Date(dateString).toLocaleString("vi-VN")
}

// Tự động refresh danh sách users và files mỗi 60 giây
setInterval(() => {
  loadUsers()
  loadReceivedFiles()
}, 60000)
