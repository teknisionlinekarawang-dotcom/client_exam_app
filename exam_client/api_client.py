import requests
import json
from config import ClientConfig

class APIClient:
    def __init__(self):
        self.config = ClientConfig()
        self.token = None
        self.base_url = self.config.get_server_url()
        self.api_version = self.config.config.get('api_version', 'v1')
    
    def check_connection(self):
        """Cek konektivitas ke server"""
        try:
            response = requests.get(
                f'{self.base_url}/api/{self.api_version}/health',
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def login(self, student_id, password):
        """Login dengan student_id dan password"""
        try:
            response = requests.post(
                f'{self.base_url}/api/{self.api_version}/login',
                json={'student_id': student_id, 'password': password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                return True, data.get('message', 'Login berhasil')
            else:
                data = response.json()
                return False, data.get('message', 'Login gagal')
        except requests.exceptions.Timeout:
            return False, 'Koneksi timeout'
        except requests.exceptions.ConnectionError:
            return False, 'Tidak dapat terhubung ke server'
        except Exception as e:
            return False, f'Error: {str(e)}'
    
    def update_server_config(self, host, port):
        """Update konfigurasi server"""
        new_config = self.config.config.copy()
        new_config['server_host'] = host
        new_config['server_port'] = int(port)
        
        if self.config.save_config(new_config):
            self.base_url = self.config.get_server_url()
            return True
        return False