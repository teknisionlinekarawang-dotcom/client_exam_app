import json
import os

class ClientConfig:
    CONFIG_FILE = 'server_config.json'
    
    DEFAULT_CONFIG = {
        'server_host': 'localhost',
        'server_port': 5000,
        'api_version': 'v1'
    }
    
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self):
        """Load konfigurasi dari file, atau gunakan default"""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()
    
    def save_config(self, new_config):
        """Simpan konfigurasi ke file"""
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(new_config, f, indent=4)
            self.config = new_config
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_server_url(self):
        """Dapatkan URL server lengkap"""
        host = self.config.get('server_host', 'localhost')
        port = self.config.get('server_port', 5000)
        return f'http://{host}:{port}'