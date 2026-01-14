"""
Twelve Data API ile BIST hisse senedi verisi çekme
"""
import os
import streamlit as st
from typing import Optional, Dict
from datetime import datetime
from twelvedata import TDClient


def get_twelvedata_client():
    """Twelve Data client'ı al (API key ile)"""
    try:
        # Streamlit Cloud'da secrets'tan al
        import streamlit as st
        if 'twelvedata' in st.secrets:
            api_key = st.secrets['twelvedata']['api_key']
        else:
            # Local'de .env'den al
            api_key = os.getenv('TWELVEDATA_API_KEY')
        
        if not api_key:
            st.error("❌ Twelve Data API key bulunamadı. Lütfen secrets'ı kontrol edin.")
            return None
        
        return TDClient(apikey=api_key)
    except Exception as e:
        st.error(f"❌ Twelve Data client oluşturulamadı: {str(e)}")
        return None


@st.cache_data(ttl=300)  # 5 dakika cache
def get_stock_price(symbol: str) -> Optional[float]:
    """
    Hisse senedi için güncel fiyat getir (Twelve Data API)
    
    Args:
        symbol: BIST ticker sembolü (örn: "THYAO.IS" veya "THYAO")
    
    Returns:
        Güncel fiyat veya None (hata durumunda)
    """
    try:
        # BIST hisseleri için Twelve Data formatı: .BIST
        original_symbol = symbol
        
        # .IS'yi temizle ve .BIST ekle
        symbol = symbol.upper().replace('.IS', '')
        symbol = f"{symbol}.BIST"
        
        # Twelve Data client
        td = get_twelvedata_client()
        if not td:
            return None
        
        # Fiyat çek
        ts = td.time_series(
            symbol=symbol,
            interval="1day",
            outputsize=1,
            timezone="Europe/Istanbul"
        )
        
        data = ts.as_json()
        
        if not data or len(data) == 0:
            st.warning(f"⚠️ {original_symbol} için veri bulunamadı. Lütfen ticker'ı kontrol edin.")
            return None
        
        # En son fiyat
        latest = data[0]
        price = float(latest['close'])
        
        # Debug mode
        if st.session_state.get('debug_mode', False):
            date_str = latest.get('datetime', 'N/A')
            st.caption(f"📊 **{original_symbol}**: ₺{price:.2f} (Twelve Data - {symbol} - {date_str})")
        
        return price
    
    except Exception as e:
        error_msg = str(e)
        
        # Rate limit kontrolü
        if 'usage limit' in error_msg.lower() or 'quota' in error_msg.lower():
            st.error(f"⚠️ **Twelve Data günlük limiti doldu.** Yarın yeniden deneyin.")
        else:
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
        # .IS'yi temizle ve .BIST ekle
        original_symbol = symbol
        symbol = symbol.upper().replace('.IS', '')
        symbol = f"{symbol}.BIST"
        
        td = get_twelvedata_client()
        if not td:
            return {
                'symbol': original_symbol,
                'longName': original_symbol,
                'currentPrice': get_stock_price(original_symbol),
            }
        
        # Quote bilgilerini al
        quote = td.quote(symbol=symbol).as_json()
        
        return {
            'symbol': original_symbol,
            'longName': quote.get('name', original_symbol),
            'currentPrice': float(quote.get('close', 0)),
            'previousClose': float(quote.get('previous_close', 0)),
            'dayHigh': float(quote.get('high', 0)),
            'dayLow': float(quote.get('low', 0)),
            'volume': int(quote.get('volume', 0)),
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

