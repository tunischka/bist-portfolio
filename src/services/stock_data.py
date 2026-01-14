"""
TradingView (tvDatafeed) ile BIST hisse senedi verisi çekme
"""
import streamlit as st
from typing import Optional, Dict
from datetime import datetime
from tvDatafeed import TvDatafeed, Interval


# TradingView client (global, tek instance)
_tv_client = None

def get_tv_client():
    """TradingView client'ı al"""
    global _tv_client
    if _tv_client is None:
        # Username/password gerektirmiyor - anonim kullanım
        _tv_client = TvDatafeed()
    return _tv_client


@st.cache_data(ttl=300)  # 5 dakika cache
def get_stock_price(symbol: str) -> Optional[float]:
    """
    Hisse senedi için güncel fiyat getir (TradingView API)
    
    Args:
        symbol: BIST ticker sembolü (örn: "THYAO" veya "THYAO.IS")
    
    Returns:
        Güncel fiyat veya None (hata durumunda)
    """
    try:
        # Symbol formatı temizle (sadece ticker kalsın)
        original_symbol = symbol
        symbol = symbol.upper().replace('.IS', '').replace('.BIST', '')
        
        # TradingView client
        tv = get_tv_client()
        
        # BIST verisini çek (exchange='BIST', 1 günlük data yeterli)
        data = tv.get_hist(
            symbol=symbol,
            exchange='BIST',
            interval=Interval.in_daily,
            n_bars=1
        )
        
        if data is None or data.empty:
            st.warning(f"⚠️ {original_symbol} için veri bulunamadı. Lütfen ticker'ı kontrol edin.")
            return None
        
        # En son kapanış fiyatı
        price = float(data['close'].iloc[-1])
        
        # Debug mode
        if st.session_state.get('debug_mode', False):
            date_str = data.index[-1].strftime('%Y-%m-%d')
            st.caption(f"📊 **{original_symbol}**: ₺{price:.2f} (TradingView - BIST:{symbol} - {date_str})")
        
        return price
    
    except Exception as e:
        error_msg = str(e)
        st.error(f"❌ Fiyat alınamadı ({original_symbol}): {error_msg}")
        return None


@st.cache_data(ttl=300)  # 5 dakika cache
def get_stock_info(symbol: str) -> Dict:
    """
    Hisse senedi için detaylı bilgi getir
    
    Args:
        symbol: BIST ticker sembolü
    
    Returns:
        Hisse bilgileri dict
    """
    try:
        original_symbol = symbol
        symbol = symbol.upper().replace('.IS', '').replace('.BIST', '')
        
        tv = get_tv_client()
        
        # OHLCV verisi çek (5 gün)
        data = tv.get_hist(
            symbol=symbol,
            exchange='BIST',
            interval=Interval.in_daily,
            n_bars=5
        )
        
        if data is None or data.empty:
            return {
                'symbol': original_symbol,
                'longName': original_symbol,
                'currentPrice': get_stock_price(original_symbol),
            }
        
        # Son gün ve önceki gün
        latest = data.iloc[-1]
        previous = data.iloc[-2] if len(data) > 1 else latest
        
        return {
            'symbol': original_symbol,
            'longName': f"BIST:{symbol}",
            'currentPrice': float(latest['close']),
            'previousClose': float(previous['close']),
            'dayHigh': float(latest['high']),
            'dayLow': float(latest['low']),
            'volume': int(latest['volume']),
        }
    
    except Exception:
        # Hata durumunda basit veri döndür
        return {
            'symbol': original_symbol,
            'longName': original_symbol,
            'currentPrice': get_stock_price(original_symbol),
        }


def validate_bist_symbol(symbol: str) -> bool:
    """
    BIST sembolünün geçerli olup olmadığını kontrol et
    
    Args:
        symbol: Kontrol edilecek sembol
    
    Returns:
        True/False
    """
    price = get_stock_price(symbol)
    return price is not None and price > 0
