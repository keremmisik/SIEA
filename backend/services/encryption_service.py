from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json
import os
from decouple import config
from typing import Any, Dict

class EncryptionService:
    def __init__(self):
        # Encryption key'i environment variable'dan al veya oluştur
        self.encryption_key = self._get_or_create_key()
        self.fernet = Fernet(self.encryption_key)
    
    def _get_or_create_key(self) -> bytes:
        """Şifreleme anahtarını al veya oluştur"""
        key_string = config('ENCRYPTION_KEY', default=None)
        
        if key_string:
            return key_string.encode()
        else:
            # Yeni anahtar oluştur (production'da bu manuel yapılmalı)
            key = Fernet.generate_key()
            print(f"Generated new encryption key: {key.decode()}")
            print("Please add this to your .env file as ENCRYPTION_KEY")
            return key
    
    def encrypt_data(self, data: Any) -> str:
        """Veriyi şifrele"""
        try:
            # Veriyi JSON string'e çevir
            json_data = json.dumps(data, ensure_ascii=False, default=str)
            
            # UTF-8 bytes'a çevir
            data_bytes = json_data.encode('utf-8')
            
            # Şifrele
            encrypted_data = self.fernet.encrypt(data_bytes)
            
            # Base64 encode et
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Encryption failed: {str(e)}")
    
    def decrypt_data(self, encrypted_data: str) -> Any:
        """Şifrelenmiş veriyi çöz"""
        try:
            # Base64 decode et
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # Şifreyi çöz
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            
            # UTF-8 string'e çevir
            json_data = decrypted_bytes.decode('utf-8')
            
            # JSON'dan Python objesine çevir
            return json.loads(json_data)
            
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")
    
    def encrypt_file(self, file_path: str) -> str:
        """Dosyayı şifrele"""
        try:
            with open(file_path, 'rb') as file:
                file_data = file.read()
            
            encrypted_data = self.fernet.encrypt(file_data)
            
            # Şifrelenmiş dosyayı kaydet
            encrypted_path = f"{file_path}.encrypted"
            with open(encrypted_path, 'wb') as encrypted_file:
                encrypted_file.write(encrypted_data)
            
            # Orijinal dosyayı sil
            os.remove(file_path)
            
            return encrypted_path
            
        except Exception as e:
            raise Exception(f"File encryption failed: {str(e)}")
    
    def decrypt_file(self, encrypted_file_path: str, output_path: str) -> str:
        """Şifrelenmiş dosyayı çöz"""
        try:
            with open(encrypted_file_path, 'rb') as encrypted_file:
                encrypted_data = encrypted_file.read()
            
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            with open(output_path, 'wb') as output_file:
                output_file.write(decrypted_data)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"File decryption failed: {str(e)}")
    
    def hash_data(self, data: str) -> str:
        """Veriyi hash'le (tek yönlü)"""
        digest = hashes.Hash(hashes.SHA256())
        digest.update(data.encode('utf-8'))
        return base64.b64encode(digest.finalize()).decode('utf-8')
