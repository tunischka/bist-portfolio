"""
Portföy hesaplama mantığı - Transaction history'den portföy durumunu hesapla
"""
from typing import List, Dict
from collections import defaultdict

from ..db.models import Transaction
from .stock_data import get_stock_price


class Position:
    """Bir hisse senedi pozisyonu"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.quantity = 0.0
        self.total_cost = 0.0  # Toplam maliyet (komisyonlar dahil)
        self.avg_cost = 0.0  # Ağırlıklı ortalama maliyet
    
    def add_buy(self, quantity: float, price: float, commission: float = 0.0):
        """Alım işlemi ekle"""
        cost = (quantity * price) + commission
        self.total_cost += cost
        self.quantity += quantity
        
        # Ağırlıklı ortalama maliyeti güncelle
        if self.quantity > 0:
            self.avg_cost = self.total_cost / self.quantity
    
    def add_sell(self, quantity: float, price: float, commission: float = 0.0):
        """Satım işlemi ekle"""
        if quantity > self.quantity:
            raise ValueError(f"Satış miktarı mevcut pozisyondan fazla: {quantity} > {self.quantity}")
        
        # Satılan kısım için maliyeti düş
        sold_cost = quantity * self.avg_cost
        self.total_cost -= sold_cost
        self.quantity -= quantity
        
        # Komisyon ekle (satış komisyonu)
        self.total_cost += commission
        
        # Ağırlıklı ortalamayı güncelle
        if self.quantity > 0:
            self.avg_cost = self.total_cost / self.quantity
        else:
            self.avg_cost = 0.0
            self.total_cost = 0.0
    
    def get_current_value(self, current_price: float) -> float:
        """Güncel değer"""
        return self.quantity * current_price
    
    def get_profit_loss(self, current_price: float) -> float:
        """Kâr/Zarar"""
        if self.quantity == 0:
            return 0.0
        current_value = self.get_current_value(current_price)
        position_cost = self.quantity * self.avg_cost
        return current_value - position_cost
    
    def get_profit_loss_percent(self, current_price: float) -> float:
        """Kâr/Zarar yüzdesi"""
        if self.quantity == 0 or self.avg_cost == 0:
            return 0.0
        return ((current_price - self.avg_cost) / self.avg_cost) * 100


class PortfolioCalculator:
    """Portföy hesaplama servisi"""
    
    @staticmethod
    def calculate_positions(transactions: List[Transaction]) -> Dict[str, Position]:
        """
        Transaction history'den mevcut pozisyonları hesapla
        
        Args:
            transactions: İşlem listesi (tarih sıralı)
        
        Returns:
            Sembol -> Position mapping
        """
        positions = defaultdict(lambda: Position(''))
        
        for txn in transactions:
            symbol = txn.symbol.upper()
            
            if symbol not in positions:
                positions[symbol] = Position(symbol)
            
            position = positions[symbol]
            
            if txn.transaction_type.upper() == 'BUY':
                position.add_buy(txn.quantity, txn.price, txn.commission)
            elif txn.transaction_type.upper() == 'SELL':
                try:
                    position.add_sell(txn.quantity, txn.price, txn.commission)
                except ValueError as e:
                    # Satış miktarı fazla - bu bir veri hatası
                    print(f"Hata: {e}")
                    continue
        
        # Sıfır pozisyonları filtrele
        active_positions = {
            symbol: pos for symbol, pos in positions.items()
            if pos.quantity > 0
        }
        
        return active_positions
    
    @staticmethod
    def get_portfolio_summary(positions: Dict[str, Position]) -> Dict:
        """
        Portföy özeti hesapla (güncel fiyatlarla)
        
        Returns:
            {
                'total_value': float,
                'total_cost': float,
                'total_profit_loss': float,
                'total_profit_loss_percent': float,
                'positions_count': int
            }
        """
        total_value = 0.0
        total_cost = 0.0
        
        for symbol, position in positions.items():
            current_price = get_stock_price(symbol)
            if current_price is None:
                continue
            
            total_value += position.get_current_value(current_price)
            total_cost += position.quantity * position.avg_cost
        
        profit_loss = total_value - total_cost
        profit_loss_percent = ((profit_loss / total_cost) * 100) if total_cost > 0 else 0.0
        
        return {
            'total_value': total_value,
            'total_cost': total_cost,
            'total_profit_loss': profit_loss,
            'total_profit_loss_percent': profit_loss_percent,
            'positions_count': len(positions)
        }
