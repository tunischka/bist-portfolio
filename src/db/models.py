"""
Veri modelleri - Firestore document yapılarını temsil eder
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """Kullanıcı modeli"""
    user_id: str
    email: str
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Firestore'a kaydetmek için dict'e çevir"""
        return {
            'email': self.email,
            'created_at': self.created_at
        }
    
    @staticmethod
    def from_dict(user_id: str, data: dict) -> 'User':
        """Firestore'dan gelen veriyi User objesine çevir"""
        return User(
            user_id=user_id,
            email=data.get('email', ''),
            created_at=data.get('created_at', datetime.now())
        )


@dataclass
class Portfolio:
    """Portföy modeli"""
    portfolio_id: str
    user_id: str
    name: str
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Firestore'a kaydetmek için dict'e çevir"""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'created_at': self.created_at
        }
    
    @staticmethod
    def from_dict(portfolio_id: str, data: dict) -> 'Portfolio':
        """Firestore'dan gelen veriyi Portfolio objesine çevir"""
        return Portfolio(
            portfolio_id=portfolio_id,
            user_id=data.get('user_id', ''),
            name=data.get('name', ''),
            created_at=data.get('created_at', datetime.now())
        )


@dataclass
class Transaction:
    """İşlem modeli (Alım/Satım)"""
    transaction_id: str
    portfolio_id: str
    symbol: str  # Örn: "THYAO.IS"
    transaction_type: str  # "BUY" veya "SELL"
    quantity: float
    price: float  # Birim fiyat
    commission: float = 0.0
    transaction_date: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Firestore'a kaydetmek için dict'e çevir"""
        return {
            'portfolio_id': self.portfolio_id,
            'symbol': self.symbol.upper(),
            'transaction_type': self.transaction_type.upper(),
            'quantity': self.quantity,
            'price': self.price,
            'commission': self.commission,
            'transaction_date': self.transaction_date,
            'created_at': self.created_at
        }
    
    @staticmethod
    def from_dict(transaction_id: str, data: dict) -> 'Transaction':
        """Firestore'dan gelen veriyi Transaction objesine çevir"""
        return Transaction(
            transaction_id=transaction_id,
            portfolio_id=data.get('portfolio_id', ''),
            symbol=data.get('symbol', ''),
            transaction_type=data.get('transaction_type', 'BUY'),
            quantity=data.get('quantity', 0.0),
            price=data.get('price', 0.0),
            commission=data.get('commission', 0.0),
            transaction_date=data.get('transaction_date', datetime.now()),
            created_at=data.get('created_at', datetime.now())
        )
    
    @property
    def total_cost(self) -> float:
        """Toplam maliyet (fiyat * miktar + komisyon)"""
        return (self.price * self.quantity) + self.commission
