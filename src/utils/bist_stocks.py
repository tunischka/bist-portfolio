"""
BIST hisse senetleri listesi ve yardımcı fonksiyonlar
"""

# Popüler BIST hisseleri
BIST_STOCKS = {
    'THYAO': 'Türk Hava Yolları',
    'GARAN': 'Garanti BBVA',
    'ISCTR': 'İş Bankası (C)',
    'AKBNK': 'Akbank',
    'TUPRS': 'Tüpraş',
    'SAHOL': 'Sabancı Holding',
    'EREGL': 'Ereğli Demir Çelik',
    'ARCLK': 'Arçelik',
    'ASELS': 'Aselsan',
    'BIMAS': 'BİM',
    'EKGYO': 'Emlak Konut GYO',
    'ENKAI': 'Enka İnşaat',
    'HALKB': 'Halkbank',
    'KCHOL': 'Koç Holding',
    'KRDMD': 'Kardemir (D)',
    'PETKM': 'Petkim',
    'SASA': 'Sasa Polyester',
    'SISE': 'Şişe Cam',
    'SOKM': 'Şok Marketler',
    'TAVHL': 'TAV Havalimanları',
    'TCELL': 'Turkcell',
    'TKFEN': 'Tekfen Holding',
    'TOASO': 'Tofaş',
    'TTKOM': 'Türk Telekom',
    'VAKBN': 'Vakıfbank',
    'VESBE': 'Vestel Beyaz Eşya',
    'YKBNK': 'Yapı Kredi',
}


def get_stock_display_name(symbol: str) -> str:
    """
    Hisse sembolü için görünen isim döndür
    
    Args:
        symbol: Hisse sembolü (örn: THYAO)
    
    Returns:
        Formatlanmış isim (örn: "📊 THYAO - Türk Hava Yolları")
    """
    name = BIST_STOCKS.get(symbol.upper(), symbol.upper())
    return f"📊 {symbol.upper()} - {name}"


def search_stocks(query: str) -> dict:
    """
    Arama sorgusuna göre hisseleri filtrele
    
    Args:
        query: Arama metni
    
    Returns:
        Filtrelenmiş hisse dict'i
    """
    if not query:
        return BIST_STOCKS
    
    query = query.upper()
    return {
        symbol: name 
        for symbol, name in BIST_STOCKS.items()
        if query in symbol or query.lower() in name.lower()
    }
