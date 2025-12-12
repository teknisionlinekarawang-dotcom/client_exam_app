import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from api_client import APIClient
from config import ClientConfig

class ExamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Ujian Digital")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        self.api_client = APIClient()
        self.is_connected = False
        
        # Frame untuk status dan settings
        self.top_frame = tk.Frame(root, bg='#f0f0f0', height=50)
        self.top_frame.pack(fill=tk.X, padx=0, pady=0)
        self.top_frame.pack_propagate(False)
        
        # Status Indikator
        self.status_canvas = tk.Canvas(self.top_frame, width=20, height=20, bg='#f0f0f0', 
                                       highlightthickness=0)
        self.status_canvas.pack(side=tk.LEFT, padx=15, pady=15)
        self.status_circle = self.status_canvas.create_oval(2, 2, 18, 18, 
                                                             fill='gray', outline='black')
        
        # Status Text
        self.status_label = tk.Label(self.top_frame, text="Disconnected", 
                                     bg='#f0f0f0', font=('Arial', 10))
        self.status_label.pack(side=tk.LEFT, padx=5, pady=15)
        
        # Settings Button (Gear Icon)
        self.settings_btn = tk.Button(self.top_frame, text="⚙️ Settings", 
                                      command=self.open_settings, 
                                      bg='#e0e0e0', font=('Arial', 10))
        self.settings_btn.pack(side=tk.RIGHT, padx=15, pady=10)
        
        # Main Content Frame
        self.content_frame = tk.Frame(root)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Placeholder untuk page saat ini
        self.current_page = None
        
        # Tampilkan login page
        self.show_login_page()
        
        # Mulai thread untuk monitoring konektivitas
        self.start_connection_monitor()
    
    def show_login_page(self):
        """Tampilkan halaman login"""
        # Hapus page sebelumnya
        if self.current_page:
            self.current_page.destroy()
        
        self.current_page = tk.Frame(self.content_frame)
        self.current_page.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = tk.Label(self.current_page, text="LOGIN", font=('Arial', 18, 'bold'))
        title.pack(pady=20)
        
        # Student ID
        tk.Label(self.current_page, text="Student ID:", font=('Arial', 12)).pack(anchor='w')
        self.student_id_entry = tk.Entry(self.current_page, font=('Arial', 11), width=30)
        self.student_id_entry.pack(pady=(0, 15), fill=tk.X)
        
        # Password
        tk.Label(self.current_page, text="Password:", font=('Arial', 12)).pack(anchor='w')
        self.password_entry = tk.Entry(self.current_page, font=('Arial', 11), 
                                       width=30, show='*')
        self.password_entry.pack(pady=(0, 20), fill=tk.X)
        
        # Login Button
        login_btn = tk.Button(self.current_page, text="LOGIN", font=('Arial', 12), 
                             bg='#4CAF50', fg='white', height=2,
                             command=self.do_login)
        login_btn.pack(fill=tk.X)
        
        # Bind Enter key
        self.password_entry.bind('<Return>', lambda e: self.do_login())
    
    def do_login(self):
        """Proses login"""
        student_id = self.student_id_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not student_id or not password:
            messagebox.showerror("Error", "Student ID dan Password tidak boleh kosong")
            return
        
        # Disable tombol untuk mencegah double click
        self.settings_btn.config(state=tk.DISABLED)
        
        # Jalankan login di thread terpisah
        thread = threading.Thread(target=self._login_thread, args=(student_id, password))
        thread.daemon = True
        thread.start()
    
    def _login_thread(self, student_id, password):
        """Login thread"""
        success, message = self.api_client.login(student_id, password)
        
        if success:
            messagebox.showinfo("Success", message)
            self.show_dashboard_page()
        else:
            messagebox.showerror("Login Failed", message)
        
        self.settings_btn.config(state=tk.NORMAL)
    
    def show_dashboard_page(self):
        """Tampilkan halaman dashboard setelah login"""
        if self.current_page:
            self.current_page.destroy()
        
        self.current_page = tk.Frame(self.content_frame)
        self.current_page.pack(fill=tk.BOTH, expand=True)
        
        title = tk.Label(self.current_page, text="DASHBOARD", font=('Arial', 18, 'bold'))
        title.pack(pady=20)
        
        message = tk.Label(self.current_page, 
                          text="Selamat datang! Aplikasi ujian digital siap digunakan.",
                          font=('Arial', 12))
        message.pack(pady=20)
        
        # Logout Button
        logout_btn = tk.Button(self.current_page, text="LOGOUT", font=('Arial', 12),
                              bg='#f44336', fg='white', height=2,
                              command=self.logout)
        logout_btn.pack(fill=tk.X)
    
    def logout(self):
        """Logout dan kembali ke login page"""
        self.api_client.token = None
        self.show_login_page()
    
    def open_settings(self):
        """Buka dialog settings"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Server Settings")
        settings_window.geometry("400x250")
        settings_window.resizable(False, False)
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Title
        title = tk.Label(settings_window, text="Server Configuration", 
                        font=('Arial', 14, 'bold'))
        title.pack(pady=15)
        
        # Host
        tk.Label(settings_window, text="Server Host:", font=('Arial', 11)).pack(anchor='w', padx=20)
        host_entry = tk.Entry(settings_window, font=('Arial', 10), width=35)
        host_entry.insert(0, self.api_client.config.config.get('server_host'))
        host_entry.pack(pady=(0, 15), padx=20, fill=tk.X)
        
        # Port
        tk.Label(settings_window, text="Server Port:", font=('Arial', 11)).pack(anchor='w', padx=20)
        port_entry = tk.Entry(settings_window, font=('Arial', 10), width=35)
        port_entry.insert(0, str(self.api_client.config.config.get('server_port')))
        port_entry.pack(pady=(0, 20), padx=20, fill=tk.X)
        
        # Buttons
        button_frame = tk.Frame(settings_window)
        button_frame.pack(fill=tk.X, padx=20, pady=15)
        
        def save_settings():
            host = host_entry.get().strip()
            port = port_entry.get().strip()
            
            if not host or not port:
                messagebox.showerror("Error", "Host dan Port tidak boleh kosong")
                return
            
            try:
                port_int = int(port)
                if self.api_client.update_server_config(host, port_int):
                    messagebox.showinfo("Success", "Konfigurasi server berhasil disimpan")
                    settings_window.destroy()
                else:
                    messagebox.showerror("Error", "Gagal menyimpan konfigurasi")
            except ValueError:
                messagebox.showerror("Error", "Port harus berupa angka")
        
        save_btn = tk.Button(button_frame, text="Save", command=save_settings, 
                            bg='#4CAF50', fg='white', width=12)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=settings_window.destroy,
                              bg='#f44336', fg='white', width=12)
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def start_connection_monitor(self):
        """Monitor konektivitas ke server secara berkala"""
        thread = threading.Thread(target=self._monitor_connection, daemon=True)
        thread.daemon = True
        thread.start()
    
    def _monitor_connection(self):
        """Thread untuk monitoring konektivitas"""
        while True:
            time.sleep(3)  # Check setiap 3 detik
            connected = self.api_client.check_connection()
            self.update_status(connected)
    
    def update_status(self, connected):
        """Update status indikator"""
        self.is_connected = connected
        color = '#4CAF50' if connected else '#f44336'  # Hijau atau Merah
        status_text = "Connected" if connected else "Disconnected"
        
        self.status_canvas.itemconfig(self.status_circle, fill=color)
        self.status_label.config(text=status_text)

if __name__ == '__main__':
    root = tk.Tk()
    app = ExamApp(root)
    root.mainloop()