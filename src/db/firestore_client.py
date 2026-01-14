"""
Firebase Firestore istemcisi - Singleton pattern ile tek instance kullanımı
"""
import os
from typing import Optional
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import Client


class FirestoreClient:
    """Firestore bağlantı yöneticisi - Singleton"""
    
    _instance: Optional['FirestoreClient'] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Firebase'i başlat (sadece bir kez çalışır)"""
        if self._client is None:
            self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Firebase Admin SDK'yı başlat"""
        try:
            # Zaten başlatılmış mı kontrol et
            firebase_admin.get_app()
        except ValueError:
            # Henüz başlatılmamış, şimdi başlat
            try:
                # Streamlit Cloud mode check
                import streamlit as st
                if 'firebase' in st.secrets:
                    # Cloud mode - streamlit secrets kullan
                    cred = credentials.Certificate(dict(st.secrets['firebase']))
                else:
                    # Local mode - JSON dosyası kullan
                    cred_path = os.getenv(
                        'FIREBASE_CREDENTIALS_PATH',
                        'serviceAccountKey.json'
                    )
                    
                    if not os.path.exists(cred_path):
                        raise FileNotFoundError(
                            f"Firebase credentials dosyası bulunamadı: {cred_path}\n"
                            f"Lütfen serviceAccountKey.json dosyasını projeye ekleyin."
                        )
                    
                    cred = credentials.Certificate(cred_path)
            except ImportError:
                # Streamlit yüklü değil - sadece local mode
                cred_path = os.getenv(
                    'FIREBASE_CREDENTIALS_PATH',
                    'serviceAccountKey.json'
                )
                
                if not os.path.exists(cred_path):
                    raise FileNotFoundError(
                        f"Firebase credentials dosyası bulunamadı: {cred_path}\n"
                        f"Lütfen serviceAccountKey.json dosyasını projeye ekleyin."
                    )
                
                cred = credentials.Certificate(cred_path)
            
            firebase_admin.initialize_app(cred)
        
        self._client = firestore.client()
    
    @property
    def db(self) -> Client:
        """Firestore client'ı döndür"""
        if self._client is None:
            self._initialize_firebase()
        return self._client


def get_firestore_client() -> Client:
    """Firestore client instance'ını al (kullanımı kolaylaştırmak için)"""
    return FirestoreClient().db
