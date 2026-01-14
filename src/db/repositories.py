"""
Repository pattern - Veritabanı işlemlerini soyutla
"""
from typing import List, Optional
from datetime import datetime
from google.cloud.firestore_v1 import Client

from .models import User, Portfolio, Transaction
from .firestore_client import get_firestore_client


class UserRepository:
    """Kullanıcı veri erişim katmanı"""
    
    def __init__(self, db: Optional[Client] = None):
        self.db = db or get_firestore_client()
        self.collection = self.db.collection('users')
    
    def create(self, user: User) -> str:
        """Yeni kullanıcı oluştur"""
        doc_ref = self.collection.document()
        user.user_id = doc_ref.id
        doc_ref.set(user.to_dict())
        return doc_ref.id
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """ID'ye göre kullanıcı getir"""
        doc = self.collection.document(user_id).get()
        if doc.exists:
            return User.from_dict(doc.id, doc.to_dict())
        return None
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Email'e göre kullanıcı getir"""
        docs = self.collection.where('email', '==', email).limit(1).stream()
        for doc in docs:
            return User.from_dict(doc.id, doc.to_dict())
        return None
    
    def email_exists(self, email: str) -> bool:
        """Email zaten kayıtlı mı kontrol et"""
        return self.get_by_email(email) is not None


class PortfolioRepository:
    """Portföy veri erişim katmanı"""
    
    def __init__(self, db: Optional[Client] = None):
        self.db = db or get_firestore_client()
        self.collection = self.db.collection('portfolios')
    
    def create(self, portfolio: Portfolio) -> str:
        """Yeni portföy oluştur"""
        doc_ref = self.collection.document()
        portfolio.portfolio_id = doc_ref.id
        doc_ref.set(portfolio.to_dict())
        return doc_ref.id
    
    def get_by_id(self, portfolio_id: str) -> Optional[Portfolio]:
        """ID'ye göre portföy getir"""
        doc = self.collection.document(portfolio_id).get()
        if doc.exists:
            return Portfolio.from_dict(doc.id, doc.to_dict())
        return None
    
    def get_by_user(self, user_id: str) -> List[Portfolio]:
        """Kullanıcının tüm portföylerini getir"""
        docs = self.collection.where('user_id', '==', user_id).order_by('created_at', direction='DESCENDING').stream()
        return [Portfolio.from_dict(doc.id, doc.to_dict()) for doc in docs]
    
    def update(self, portfolio_id: str, name: str) -> bool:
        """Portföy ismini güncelle"""
        try:
            self.collection.document(portfolio_id).update({'name': name})
            return True
        except Exception:
            return False
    
    def delete(self, portfolio_id: str) -> bool:
        """Portföy sil"""
        try:
            self.collection.document(portfolio_id).delete()
            return True
        except Exception:
            return False


class TransactionRepository:
    """İşlem veri erişim katmanı"""
    
    def __init__(self, db: Optional[Client] = None):
        self.db = db or get_firestore_client()
        self.collection = self.db.collection('transactions')
    
    def create(self, transaction: Transaction) -> str:
        """Yeni işlem oluştur"""
        doc_ref = self.collection.document()
        transaction.transaction_id = doc_ref.id
        doc_ref.set(transaction.to_dict())
        return doc_ref.id
    
    def get_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """ID'ye göre işlem getir"""
        doc = self.collection.document(transaction_id).get()
        if doc.exists:
            return Transaction.from_dict(doc.id, doc.to_dict())
        return None
    
    def get_by_portfolio(self, portfolio_id: str) -> List[Transaction]:
        """Portföye ait tüm işlemleri getir (tarih sıralı)"""
        docs = self.collection.where(
            'portfolio_id', '==', portfolio_id
        ).order_by('transaction_date', direction='ASCENDING').stream()
        return [Transaction.from_dict(doc.id, doc.to_dict()) for doc in docs]
    
    def get_by_portfolio_and_symbol(self, portfolio_id: str, symbol: str) -> List[Transaction]:
        """Belirli bir hisse senedi için işlemleri getir"""
        docs = self.collection.where('portfolio_id', '==', portfolio_id).where(
            'symbol', '==', symbol.upper()
        ).order_by('transaction_date', direction='ASCENDING').stream()
        return [Transaction.from_dict(doc.id, doc.to_dict()) for doc in docs]
    
    def delete(self, transaction_id: str) -> bool:
        """İşlem sil"""
        try:
            self.collection.document(transaction_id).delete()
            return True
        except Exception:
            return False
