import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QMessageBox, QStatusBar
)
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtCore import Qt, QTimer

# Ganti dengan IP AlmaLinux Anda!
# Jika server dan client berada di VM yang sama (Bridge Network), IP harus diakses.
SERVER_BASE_URL = "http://192.168.1.100:5000/api/v1" 

class LoginApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistem Ujian Digital")
        self.setGeometry(100, 100, 400, 300)
        
        self.api_url = SERVER_BASE_URL
        self.user_token = None
        
        self.init_ui()
        self.start_status_check()

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # --- Bagian Judul dan Indikator ---
        header_layout = QHBoxLayout()
        title_label = QLabel("Aplikasi Ujian Digital")
        title_label.setStyleSheet("font-size: 20pt; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        # Tombol Gear untuk Setting (Belum diimplementasikan logikanya, hanya tampilan)
        settings_button = QPushButton("⚙️")
        settings_button.setFixedSize(30, 30)
        settings_button.clicked.connect(self.show_settings_dialog)
        header_layout.addWidget(settings_button)
        
        main_layout.addLayout(header_layout)
        main_layout.addStretch()

        # --- Bagian Form Login ---
        
        # Input ID Siswa
        main_layout.addWidget(QLabel("ID Siswa:"))
        self.student_id_input = QLineEdit()
        self.student_id_input.setPlaceholderText("Masukkan Nomor Induk Siswa")
        main_layout.addWidget(self.student_id_input)

        # Input Password
        main_layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Masukkan Password")
        main_layout.addWidget(self.password_input)

        # Tombol Login
        self.login_button = QPushButton("LOGIN")
        self.login_button.setStyleSheet("padding: 10px; font-size: 14pt; background-color: #4CAF50; color: white;")
        self.login_button.clicked.connect(self.attempt_login)
        main_layout.addWidget(self.login_button)
        
        main_layout.addStretch()
        
        # --- Status Bar (Indikator Status Server) ---
        self.status_bar = QStatusBar(self)
        self.status_label = QLabel("Status Server: Menghubungkan...")
        self.status_bar.addWidget(self.status_label)
        
        # Indikator Visual
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("font-size: 14pt; color: gray;")
        self.status_bar.addWidget(self.status_indicator)
        
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
        status_url = f"{self.api_url}/status"
        try:
            response = requests.get(status_url, timeout=3) # Timeout 3 detik
            if response.status_code == 200 and response.json().get('status') == 'Server API Ujian Aktif':
                self.set_server_status(True)
            else:
                self.set_server_status(False, "Server merespons, namun data status tidak valid.")
        except requests.exceptions.RequestException:
            self.set_server_status(False, "Koneksi Gagal: Cek IP Server/Jaringan.")

    def set_server_status(self, is_online, message="Tersambung ke Server"):
        """Mengatur indikator visual berdasarkan status koneksi."""
        if is_online:
            self.status_indicator.setStyleSheet("font-size: 14pt; color: green;")
            self.status_label.setText(f"Status Server: {message}")
            self.login_button.setEnabled(True)
        else:
            self.status_indicator.setStyleSheet("font-size: 14pt; color: red;")
            self.status_label.setText(f"Status Server: {message}")
            self.login_button.setEnabled(False) # Nonaktifkan login jika server mati

    def attempt_login(self):
        """Mengirim data login ke Server API Flask."""
        student_id = self.student_id_input.text().strip()
        password = self.password_input.text()
        
        if not student_id or not password:
            QMessageBox.warning(self, "Peringatan", "Semua field harus diisi.")
            return

        login_data = {
            "student_id": student_id,
            "password": password
        }
        
        login_url = f"{self.api_url}/login"
        
        try:
            self.login_button.setText("LOGIN...")
            self.login_button.setEnabled(False)

            response = requests.post(login_url, json=login_data, timeout=5)

            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get('token')
                QMessageBox.information(self, "Berhasil", f"Selamat datang, {data.get('user_name')}! Token berhasil diterima.")
                
                # --- LOGIKA UNTUK MELANJUTKAN KE JENDELA UJIAN (Selanjutnya) ---
                # Di sini Anda akan menutup jendela login dan membuka jendela ujian utama
                print(f"Token JWT: {self.user_token}")
                # Contoh: self.show_exam_window() 
                
            elif response.status_code == 401:
                QMessageBox.critical(self, "Gagal", "ID Siswa atau Password salah. Silakan coba lagi.")
            else:
                QMessageBox.critical(self, "Gagal", f"Kesalahan API: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Gagal Koneksi", f"Tidak dapat terhubung ke server API. Detail: {e}")
        finally:
            self.login_button.setText("LOGIN")
            self.login_button.setEnabled(True)
            self.check_server_status() # Cek status lagi

    def show_settings_dialog(self):
        """Menampilkan dialog untuk mengubah IP Server."""
        QMessageBox.information(self, "Pengaturan", 
                                "Fitur pengaturan akan memungkinkan guru/admin mengubah IP Server API jika diperlukan.")
        # TODO: Implementasikan input dialog untuk mengubah self.api_url
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginApp()
    window.show()
    sys.exit(app.exec())
