"""
Firebase Authentication wrapper - Basit email/password auth
"""
import re
from typing import Optional, Tuple
from datetime import datetime

from ..db.models import User
from ..db.repositories import UserRepository


class AuthService:
    """Authentication servisi"""
    
    def __init__(self):
        self.user_repo = UserRepository()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Email formatını kontrol et"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        Şifre güvenliğini kontrol et
        
        Returns:
            (geçerli_mi, hata_mesajı)
        """
        if len(password) < 6:
            return False, "Şifre en az 6 karakter olmalı"
        return True, ""
    
    def register(self, email: str, password: str, confirm_password: str) -> Tuple[bool, str, Optional[User]]:
        """
        Yeni kullanıcı kaydı
        
        Returns:
            (başarılı_mı, mesaj, user)
        """
        # Email kontrolü
        if not self.validate_email(email):
            return False, "Geçersiz email formatı", None
        
        # Email zaten kayıtlı mı?
        if self.user_repo.email_exists(email):
            return False, "Bu email zaten kayıtlı", None
        
        # Şifre kontrolü
        is_valid, msg = self.validate_password(password)
        if not is_valid:
            return False, msg, None
        
        # Şifre eşleşiyor mu?
        if password != confirm_password:
            return False, "Şifreler eşleşmiyor", None
        
        # Kullanıcı oluştur
        user = User(
            user_id='',  # Repository tarafından set edilecek
            email=email,
            created_at=datetime.now()
        )
        
        # Firestore'a kaydet
        user_id = self.user_repo.create(user)
        user.user_id = user_id
        
        # Not: Gerçek bir uygulamada şifreyi hash'leyip ayrı bir tabloda saklardık
        # Bu basitleştirilmiş versiyonda şifre kontrolü yapmıyoruz (sadece demo)
        
        return True, "Kayıt başarılı! Giriş yapabilirsiniz.", user
    
    def login(self, email: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """
        Kullanıcı girişi
        
        Returns:
            (başarılı_mı, mesaj, user)
        """
        # Email kontrolü
        if not self.validate_email(email):
            return False, "Geçersiz email formatı", None
        
        # Kullanıcı var mı?
        user = self.user_repo.get_by_email(email)
        if user is None:
            return False, "Email veya şifre hatalı", None
        
        # Not: Gerçek uygulamada şifre hash kontrolü yapılır
        # Bu basitleştirilmiş versiyonda sadece email kontrolü yapıyoruz
        
        return True, "Giriş başarılı!", user
