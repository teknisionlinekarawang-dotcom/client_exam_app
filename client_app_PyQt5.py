import sys
import requests
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QMessageBox, QStatusBar,
    QSizePolicy
)
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import Qt, QTimer, QSettings

# =================================================================
# !!! PENTING: Ganti dengan IP Internal AlmaLinux VM Anda !!!
# Contoh: "http://192.168.1.100:5000/api/v1"
SERVER_BASE_URL = "http://192.168.1.100:5000/api/v1" 
# =================================================================

class LoginApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistem Ujian Digital")
        self.setGeometry(100, 100, 400, 300)
        
        # Inisialisasi pengaturan untuk menyimpan IP server
        self.settings = QSettings("DigitalExamApp", "Client")
        self.api_url = self.settings.value("api_url", SERVER_BASE_URL)
        
        self.user_token = None
        
        self.init_ui()
        self.start_status_check()
        
        # Memastikan aplikasi berjalan di tengah layar
        self.center_window()

    def center_window(self):
        """Memposisikan jendela di tengah layar."""
        qr = self.frameGeometry()
        cp = QApplication.desktop().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # --- Header dan Tombol Setting ---
        header_layout = QHBoxLayout()
        title_label = QLabel("Aplikasi Ujian Digital")
        title_label.setStyleSheet("font-size: 20pt; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        settings_button = QPushButton("⚙️")
        settings_button.setFixedSize(30, 30)
        settings_button.setToolTip("Pengaturan Server API")
        settings_button.clicked.connect(self.show_settings_dialog)
        header_layout.addWidget(settings_button)
        
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(30) # Spasi setelah judul

        # --- Form Login ---
        
        # Input ID Siswa
        main_layout.addWidget(QLabel("ID Siswa:"))
        self.student_id_input = QLineEdit()
        self.student_id_input.setPlaceholderText("Masukkan Nomor Induk Siswa (Contoh: 12345)")
        main_layout.addWidget(self.student_id_input)

        # Input Password
        main_layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Masukkan Password (Contoh: 123456)")
        main_layout.addWidget(self.password_input)
        
        # Tombol Login
        self.login_button = QPushButton("LOGIN")
        self.login_button.setStyleSheet("padding: 10px; font-size: 14pt; background-color: #007bff; color: white; border-radius: 5px;")
        self.login_button.clicked.connect(self.attempt_login)
        main_layout.addWidget(self.login_button)
        
        main_layout.addStretch()
        
        # --- Status Bar ---
        self.status_bar = QStatusBar(self)
        self.status_label = QLabel("Status Server: Menghubungkan...")
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("font-size: 14pt; color: gray;")
        
        self.status_bar.addWidget(self.status_label)
        self.status_bar.addPermanentWidget(self.status_indicator)
        
        main_layout.addWidget(self.status_bar)

        self.setLayout(main_layout)

    def start_status_check(self):
        """Memulai timer untuk mengecek status koneksi server secara berkala."""
        self.timer = QTimer()
        self.timer.setInterval(5000)  # Cek setiap 5 detik
        self.timer.timeout.connect(self.check_server_status)
        self.timer.start()
        self.check_server_status() # Cek pertama kali saat startup

    def check_server_status(self):
        """Mengecek endpoint /status di server Flask."""
        # Gunakan self.api_url yang diambil dari settings
        status_url = f"{self.api_url}/status"
        try:
            response = requests.get(status_url, timeout=3)
            if response.status_code == 200 and response.json().get('status') == 'Server API Ujian Aktif':
                self.set_server_status(True, f"Tersambung ke {self.api_url.split(':')[1].strip('/')}")
            else:
                self.set_server_status(False, "Server merespons, namun status API tidak valid.")
        except requests.exceptions.RequestException:
            self.set_server_status(False, f"Koneksi Gagal: Cek IP Server ({self.api_url.split(':')[1].strip('/')})")

    def set_server_status(self, is_online, message):
        """Mengatur indikator visual dan tombol login."""
        if is_online:
            self.status_indicator.setStyleSheet("font-size: 14pt; color: green;")
            self.status_label.setText(f"Status Server: {message}")
            self.login_button.setEnabled(True)
        else:
            self.status_indicator.setStyleSheet("font-size: 14pt; color: red;")
            self.status_label.setText(f"Status Server: {message}")
            self.login_button.setEnabled(False) 

    def attempt_login(self):
        """Mengirim data login ke Server API Flask dan menerima JWT."""
        student_id = self.student_id_input.text().strip()
        password = self.password_input.text()
        
        if not student_id or not password:
            QMessageBox.warning(self, "Peringatan", "Semua field harus diisi.")
            return

        login_data = {"student_id": student_id, "password": password}
        login_url = f"{self.api_url}/login"
        
        try:
            self.login_button.setText("Authenticating...")
            self.login_button.setEnabled(False)

            response = requests.post(login_url, json=login_data, timeout=5)
            data = response.json()

            if response.status_code == 200:
                self.user_token = data.get('token')
                QMessageBox.information(self, "Berhasil", f"Selamat datang, {data.get('user_name')}! Ujian dimulai.")
                
                # Sembunyikan jendela login dan mulai mode KIOSK/Ujian
                self.hide() 
                # TODO: Panggil fungsi untuk memulai ExamWindow (Langkah selanjutnya)
                # Contoh: self.exam_window = ExamWindow(self.user_token); self.exam_window.show()
                
            elif response.status_code == 401:
                QMessageBox.critical(self, "Gagal", "ID Siswa atau Password salah.")
            else:
                QMessageBox.critical(self, "Gagal", f"Kesalahan API: {response.status_code} - {data.get('message', 'Terjadi kesalahan.')}")
                
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Gagal Koneksi", "Tidak dapat terhubung ke server API. Pastikan IP Server sudah benar.")
        finally:
            self.login_button.setText("LOGIN")
            self.login_button.setEnabled(True)
            self.check_server_status()

    def show_settings_dialog(self):
        """Menampilkan input dialog sederhana untuk mengubah IP Server."""
        from PyQt5.QtWidgets import QInputDialog
        
        current_ip = self.api_url.split(':')[1].strip('/')
        
        new_ip, ok = QInputDialog.getText(
            self, 'Pengaturan Server', 'Masukkan IP dan Port Server API (contoh: 192.168.1.100:5000):', 
            QLineEdit.Normal, current_ip
        )

        if ok and new_ip:
            try:
                # Validasi sederhana format IP:Port
                ip_part, port_part = new_ip.split(':')
                int(port_part) # Coba konversi port ke integer
                
                new_url = f"http://{new_ip}/api/v1"
                self.api_url = new_url
                self.settings.setValue("api_url", new_url) # Simpan ke pengaturan
                QMessageBox.information(self, "Berhasil", f"IP Server diperbarui ke: {new_ip}. Melakukan pengecekan koneksi...")
                self.check_server_status()
                
            except ValueError:
                QMessageBox.critical(self, "Error", "Format IP dan Port tidak valid. Gunakan format IP:Port.")
            except Exception:
                 QMessageBox.critical(self, "Error", "Format URL tidak dikenal.")
                 
# =================================================================
# FUNGSI UTAMA (MAIN EXECUTION)
# =================================================================
if __name__ == '__main__':
    # Memastikan hanya ada satu instance aplikasi
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
        
    window = LoginApp()
    window.show()
    sys.exit(app.exec_())
