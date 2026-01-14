"""
yfinance ile BIST hisse senedi verisi çekme
"""
import yfinance as yf
import streamlit as st
from typing import Optional, Dict
from datetime import datetime, timedelta


@st.cache_data(ttl=60)  # 1 dakika cache
def get_stock_price(symbol: str) -> Optional[float]:
    """
    Hisse senedi için güncel fiyat getir
    
    Args:
        symbol: BIST ticker sembolü (örn: "THYAO.IS" veya "THYAO")
    
    Returns:
        Güncel fiyat veya None (hata durumunda)
    """
    try:
        # BIST hisseleri ".IS" ile biter
        original_symbol = symbol
        if not symbol.upper().endswith('.IS'):
            symbol = f"{symbol.upper()}.IS"
        else:
            symbol = symbol.upper()
        
        ticker = yf.Ticker(symbol)
        
        # Önce yakın tarihli veri deneyelim (5 gün)
        hist = ticker.history(period='5d')
        
        if hist.empty:
            # Alternatif: 1 ay geriye git
            hist = ticker.history(period='1mo')
        
        if hist.empty:
            # Debug için hata mesajı göster
            st.warning(f"⚠️ {symbol} için veri bulunamadı. Lütfen sembolü kontrol edin.")
            return None
        
        # En son mevcut fiyat
        latest_price = float(hist['Close'].iloc[-1])
        
        # Debug: veri tarihini göster
        latest_date = hist.index[-1].strftime('%Y-%m-%d %H:%M')
        if st.session_state.get('debug_mode', False):
            st.caption(f"📊 {original_symbol}: ₺{latest_price:.2f} (veri: {latest_date})")
        
        return latest_price
    
    except Exception as e:
        st.error(f"❌ Fiyat alınamadı ({symbol}): {str(e)}")
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
        if not symbol.upper().endswith('.IS'):
            symbol = f"{symbol.upper()}.IS"
        
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
            'symbol': symbol,
            'longName': info.get('longName', symbol),
            'currentPrice': info.get('currentPrice', get_stock_price(symbol)),
            'previousClose': info.get('previousClose', 0),
            'dayHigh': info.get('dayHigh', 0),
            'dayLow': info.get('dayLow', 0),
        }
    
    except Exception:
        # Hata durumunda basit veri döndür
        return {
            'symbol': symbol,
            'longName': symbol,
            'currentPrice': get_stock_price(symbol),
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
