import PySimpleGUI as sg
import threading
import time
import os
from api_client import APIClient
from config import ClientConfig

# Konfigurasi tema
sg.theme('DarkBlue3')
sg.set_options(font=('Arial', 11), element_padding=(10, 10))

class ExamApp:
    def __init__(self, kiosk_mode=False):
        self.api_client = APIClient()
        self.is_connected = False
        self.kiosk_mode = kiosk_mode
        self.current_window = None
        self.monitor_thread = None
        self.token = None
        
        # Mulai monitoring konektivitas
        self.start_connection_monitor()
    
    def get_status_color(self):
        """Return warna status dan text"""
        if self.is_connected:
            return ('#4CAF50', '● CONNECTED')
        else:
            return ('#f44336', '● DISCONNECTED')
    
    def create_header(self):
        """Buat header dengan status dan settings button"""
        status_color, status_text = self.get_status_color()
        
        header = [
            [
                sg.Text(status_text, font=('Arial', 11, 'bold'), 
                       text_color=status_color, key='-STATUS-TEXT-'),
                sg.Push(),
                sg.Button('⚙️ Settings', key='-SETTINGS-', 
                         button_color=('white', '#555555'), 
                         font=('Arial', 10), pad=(10, 5)),
            ]
        ]
        return header
    
    def create_login_layout(self):
        """Buat layout login page"""
        layout = [
            [sg.Push(), sg.Text('EXAM LOGIN', font=('Arial', 24, 'bold')), sg.Push()],
            [sg.Text('')],
            [sg.Text('Student ID:', font=('Arial', 12, 'bold'))],
            [sg.InputText(key='-STUDENT-ID-', size=(35, 1), font=('Arial', 12),
                         focus=True)],
            [sg.Text('')],
            [sg.Text('Password:', font=('Arial', 12, 'bold'))],
            [sg.InputText(key='-PASSWORD-', size=(35, 1), font=('Arial', 12),
                         password_char='*')],
            [sg.Text('')],
            [sg.Button('LOGIN', key='-LOGIN-', size=(20, 2),
                      button_color=('white', '#4CAF50'),
                      font=('Arial', 14, 'bold')),
             sg.Button('EXIT', key='-EXIT-', size=(10, 2),
                      button_color=('white', '#f44336'),
                      font=('Arial', 12, 'bold'))],
            [sg.Text('')],
            [sg.Text('', key='-LOGIN-MSG-', text_color='#f44336', font=('Arial', 10))],
        ]
        
        full_layout = self.create_header() + [[sg.VSeperator()]] + layout
        return full_layout
    
    def create_dashboard_layout(self, student_name=''):
        """Buat layout dashboard page"""
        layout = [
            [sg.Push(), sg.Text(f'Welcome, {student_name}!', 
                              font=('Arial', 18, 'bold')), sg.Push()],
            [sg.Text('')],
            [sg.Text('Aplikasi Ujian Digital Siap Digunakan', 
                    font=('Arial', 14), justification='center')],
            [sg.Text('')],
            [sg.Text('Status: Connected to Server', 
                    font=('Arial', 12), text_color='#4CAF50')],
            [sg.Text('')],
            [sg.Push(),
             sg.Button('START EXAM', key='-START-EXAM-', size=(20, 3),
                      button_color=('white', '#2196F3'),
                      font=('Arial', 14, 'bold')),
             sg.Push()],
            [sg.Text('')],
            [sg.Push(),
             sg.Button('LOGOUT', key='-LOGOUT-', size=(15, 2),
                      button_color=('white', '#f44336'),
                      font=('Arial', 12)),
             sg.Push()],
        ]
        
        full_layout = self.create_header() + [[sg.VSeperator()]] + layout
        return full_layout
    
    def login_window(self):
        """Tampilkan login window"""
        layout = self.create_login_layout()
        
        self.current_window = sg.Window(
            'Exam Digital - Login',
            layout,
            size=(600, 500),
            finalize=True,
            element_justification='center',
            keep_on_top=False,
            background_color='#1e1e1e'
        )
        
        while True:
            event, values = self.current_window.read(timeout=500)
            
            # Update status setiap 500ms
            status_color, status_text = self.get_status_color()
            self.current_window['-STATUS-TEXT-'].update(
                status_text, text_color=status_color
            )
            
            if event == sg.WINDOW_CLOSED or event == '-EXIT-':
                self.current_window.close()
                return False
            
            elif event == '-LOGIN-':
                student_id = values['-STUDENT-ID-'].strip()
                password = values['-PASSWORD-'].strip()
                
                if not student_id or not password:
                    self.current_window['-LOGIN-MSG-'].update(
                        'Student ID dan Password tidak boleh kosong'
                    )
                    continue
                
                # Disable login button
                self.current_window['-LOGIN-'].update(disabled=True)
                self.current_window['-LOGIN-MSG-'].update('Authenticating...')
                self.current_window.refresh()
                
                # Login di thread terpisah
                success, message = self.api_client.login(student_id, password)
                
                if success:
                    self.token = self.api_client.token
                    self.current_window.close()
                    self.dashboard_window(student_id)
                    break
                else:
                    self.current_window['-LOGIN-MSG-'].update(message)
                    self.current_window['-LOGIN-'].update(disabled=False)
            
            elif event == '-SETTINGS-':
                self.settings_window()
    
    def dashboard_window(self, student_id):
        """Tampilkan dashboard window"""
        layout = self.create_dashboard_layout(student_id)
        
        self.current_window = sg.Window(
            'Exam Digital - Dashboard',
            layout,
            size=(600, 500),
            finalize=True,
            element_justification='center',
            keep_on_top=False,
            background_color='#1e1e1e'
        )
        
        while True:
            event, values = self.current_window.read(timeout=500)
            
            # Update status
            status_color, status_text = self.get_status_color()
            self.current_window['-STATUS-TEXT-'].update(
                status_text, text_color=status_color
            )
            
            if event == sg.WINDOW_CLOSED:
                self.current_window.close()
                return
            
            elif event == '-LOGOUT-':
                self.api_client.token = None
                self.token = None
                self.current_window.close()
                break
            
            elif event == '-START-EXAM-':
                sg.popup_ok('Fitur ujian akan dikembangkan', 
                           title='Coming Soon',
                           font=('Arial', 12))
            
            elif event == '-SETTINGS-':
                self.settings_window()
    
    def settings_window(self):
        """Tampilkan settings dialog"""
        current_host = self.api_client.config.config.get('server_host')
        current_port = str(self.api_client.config.config.get('server_port'))
        
        layout = [
            [sg.Text('Server Configuration', font=('Arial', 14, 'bold'))],
            [sg.Text('')],
            [sg.Text('Server Host:', font=('Arial', 11, 'bold'))],
            [sg.InputText(default_text=current_host, key='-HOST-', 
                         size=(30, 1), font=('Arial', 11))],
            [sg.Text('')],
            [sg.Text('Server Port:', font=('Arial', 11, 'bold'))],
            [sg.InputText(default_text=current_port, key='-PORT-', 
                         size=(30, 1), font=('Arial', 11))],
            [sg.Text('')],
            [sg.Button('Save', size=(10, 1), key='-SAVE-',
                      button_color=('white', '#4CAF50')),
             sg.Button('Cancel', size=(10, 1), key='-CANCEL-',
                      button_color=('white', '#f44336'))],
            [sg.Text('', key='-SETTINGS-MSG-', text_color='#4CAF50', 
                    font=('Arial', 10))],
        ]
        
        window = sg.Window('Server Settings', layout, finalize=True,
                          element_justification='center',
                          background_color='#2a2a2a')
        
        while True:
            event, values = window.read()
            
            if event == sg.WINDOW_CLOSED or event == '-CANCEL-':
                window.close()
                break
            
            elif event == '-SAVE-':
                host = values['-HOST-'].strip()
                port = values['-PORT-'].strip()
                
                if not host or not port:
                    window['-SETTINGS-MSG-'].update(
                        'Host dan Port tidak boleh kosong',
                        text_color='#f44336'
                    )
                    continue
                
                try:
                    port_int = int(port)
                    if self.api_client.update_server_config(host, port_int):
                        window['-SETTINGS-MSG-'].update(
                            'Konfigurasi tersimpan',
                            text_color='#4CAF50'
                        )
                        window.refresh()
                        time.sleep(1)
                        window.close()
                        break
                    else:
                        window['-SETTINGS-MSG-'].update(
                            'Gagal menyimpan konfigurasi',
                            text_color='#f44336'
                        )
                except ValueError:
                    window['-SETTINGS-MSG-'].update(
                        'Port harus berupa angka',
                        text_color='#f44336'
                    )
    
    def start_connection_monitor(self):
        """Mulai thread monitoring konektivitas"""
        self.monitor_thread = threading.Thread(
            target=self._monitor_connection,
            daemon=True
        )
        self.monitor_thread.start()
    
    def _monitor_connection(self):
        """Monitor konektivitas secara berkala"""
        while True:
            time.sleep(3)  # Check setiap 3 detik
            self.is_connected = self.api_client.check_connection()
    
    def run(self):
        """Jalankan aplikasi"""
        while True:
            if not self.login_window():
                break

def main():
    """Main entry point"""
    # Tentukan apakah menggunakan kiosk mode
    # Bisa diset via environment variable: KIOSK_MODE=1 python3 main.py
    kiosk_mode = os.environ.get('KIOSK_MODE', '0') == '1'
    
    app = ExamApp(kiosk_mode=kiosk_mode)
    app.run()

if __name__ == '__main__':
    main()
