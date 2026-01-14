"""
Portföy detay sayfası - İşlemler ve pozisyonlar
"""
import streamlit as st
import pandas as pd
from datetime import datetime

from src.auth.session import SessionManager
from src.db.repositories import PortfolioRepository, TransactionRepository
from src.db.models import Transaction
from src.services.portfolio_calculator import PortfolioCalculator
from src.services.stock_data import get_stock_price, validate_bist_symbol


def show_portfolio_page():
    """Portföy detay sayfasını göster"""
    user = SessionManager.get_current_user()
    if not user:
        st.error("Lütfen giriş yapın")
        st.session_state.page = 'login'
        st.rerun()
        return
    
    # Portföy ID kontrolü
    if 'current_portfolio_id' not in st.session_state:
        st.error("Portföy bulunamadı")
        st.session_state.page = 'dashboard'
        st.rerun()
        return
    
    portfolio_id = st.session_state.current_portfolio_id
    
    # Portföyü yükle
    portfolio_repo = PortfolioRepository()
    portfolio = portfolio_repo.get_by_id(portfolio_id)
    
    if not portfolio or portfolio.user_id != user.user_id:
        st.error("Bu portföye erişim yetkiniz yok")
        st.session_state.page = 'dashboard'
        st.rerun()
        return
    
    # Header
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.title(f"📁 {portfolio.name}")
    with col2:
        # Debug mode toggle
        if 'debug_mode' not in st.session_state:
            st.session_state.debug_mode = False
        if st.button("🐛 Debug" if not st.session_state.debug_mode else "🐛 Debug ON", 
                     use_container_width=True):
            st.session_state.debug_mode = not st.session_state.debug_mode
            st.rerun()
    with col3:
        if st.button("← Geri", use_container_width=True):
            st.session_state.page = 'dashboard'
            st.rerun()
    
    # Auto-refresh her 60 saniyede bir
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔄 Kontroler")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🔄 Yenile", use_container_width=True, key="refresh_btn"):
            st.cache_data.clear()
            st.rerun()
    with col2:
        if st.button("🗑️ Cache Sil", use_container_width=True, key="clear_cache_btn"):
            st.cache_data.clear()
            st.success("Cache temizlendi!")
            st.rerun()
    
    # Version info
    st.sidebar.markdown("---")
    try:
        from src.utils.version import get_git_info
        git_info = get_git_info()
        st.sidebar.caption(f"📌 Version: `{git_info['version']}`")
        st.sidebar.caption(f"📅 Deploy: {git_info['date']}")
    except:
        st.sidebar.caption("📌 Version: dev")

    
    # İşlemleri yükle
    transaction_repo = TransactionRepository()
    transactions = transaction_repo.get_by_portfolio(portfolio_id)
    positions = PortfolioCalculator.calculate_positions(transactions)
    
    # Özet kartları
    if positions:
        summary = PortfolioCalculator.get_portfolio_summary(positions)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Toplam Değer", f"₺{summary['total_value']:,.2f}")
        with col2:
            st.metric("Toplam Maliyet", f"₺{summary['total_cost']:,.2f}")
        with col3:
            profit_delta = summary['total_profit_loss']
            st.metric("Kar/Zarar", f"₺{profit_delta:,.2f}", delta_color="normal")
        with col4:
            st.metric("%" if summary['total_profit_loss_percent'] >= 0 else "%-", 
                     f"{abs(summary['total_profit_loss_percent']):.2f}%",
                     delta_color="off")
    
    st.markdown("---")
    
    # Yeni işlem ekleme
    with st.expander("➕ Yeni İşlem Ekle", expanded=False):
        with st.form("new_transaction_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                symbol = st.text_input(
                    "Hisse Kodu",
                    placeholder="Örn: THYAO, GARAN, ISCTR"
                ).upper()
                transaction_type = st.selectbox("İşlem Tipi", ["BUY", "SELL"])
                quantity = st.number_input("Miktar (Adet)", min_value=1.0, step=1.0)
            
            with col2:
                price = st.number_input("Birim Fiyat (₺)", min_value=0.01, step=0.01, format="%.2f")
                commission = st.number_input("Komisyon (₺)", min_value=0.0, step=0.01, value=0.0, format="%.2f")
                transaction_date = st.date_input("İşlem Tarihi", value=datetime.now())
            
            submit = st.form_submit_button("İşlemi Kaydet", type="primary", use_container_width=True)
            
            if submit:
                if not symbol:
                    st.error("Lütfen hisse kodu girin")
                elif quantity <= 0 or price <= 0:
                    st.error("Miktar ve fiyat 0'dan büyük olmalı")
                else:
                    # Sembol validasyonu (opsiyonel - yavaş olabilir)
                    # if not validate_bist_symbol(symbol):
                    #     st.error(f"'{symbol}' geçerli bir BIST hissesi değil veya fiyat alınamadı")
                    # else:
                    
                    new_transaction = Transaction(
                        transaction_id='',
                        portfolio_id=portfolio_id,
                        symbol=symbol if symbol.endswith('.IS') else f"{symbol}.IS",
                        transaction_type=transaction_type,
                        quantity=quantity,
                        price=price,
                        commission=commission,
                        transaction_date=datetime.combine(transaction_date, datetime.min.time()),
                        created_at=datetime.now()
                    )
                    
                    transaction_repo.create(new_transaction)
                    st.success(f"✅ {transaction_type} işlemi kaydedildi: {quantity} adet {symbol} @ ₺{price}")
                    st.rerun()
    
    st.markdown("---")
    
    # Mevcut pozisyonlar
    st.subheader("📈 Mevcut Pozisyonlar")
    
    if not positions:
        st.info("Henüz açık pozisyon yok. Yukarıdan işlem ekleyin.")
    else:
        positions_data = []
        has_price_errors = False
        
        for symbol, position in positions.items():
            current_price = get_stock_price(symbol)
            
            if current_price is None or current_price == 0.0:
                current_price = 0.0
                has_price_errors = True
            
            profit_loss = position.get_profit_loss(current_price)
            profit_loss_percent = position.get_profit_loss_percent(current_price)
            
            # Fiyat durumuna göre renklendirme
            price_display = f"₺{current_price:.2f}" if current_price > 0 else "❌ Veri yok"
            
            positions_data.append({
                'Hisse': symbol.replace('.IS', ''),
                'Miktar': f"{position.quantity:.0f}",
                'Ort. Maliyet': f"₺{position.avg_cost:.2f}",
                'Güncel Fiyat': price_display,
                'Toplam Değer': f"₺{position.get_current_value(current_price):,.2f}",
                'Kar/Zarar': f"₺{profit_loss:,.2f}",
                '%': f"{profit_loss_percent:+.2f}%"
            })
        
        if has_price_errors:
            st.warning("⚠️ Bazı hisseler için güncel fiyat alınamadı. yfinance BIST verilerine erişemeyebilir. Debug modunu açıp detayları görebilirsiniz.")
        
        df = pd.DataFrame(positions_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # İşlem geçmişi
    st.subheader("📋 İşlem Geçmişi")
    
    if not transactions:
        st.info("Henüz işlem yok.")
    else:
        transactions_data = []
        for txn in reversed(transactions):  # En yeni en üstte
            transactions_data.append({
                'Tarih': txn.transaction_date.strftime('%d.%m.%Y'),
                'Tip': "🟢 ALIM" if txn.transaction_type == "BUY" else "🔴 SATIM",
                'Hisse': txn.symbol.replace('.IS', ''),
                'Miktar': f"{txn.quantity:.0f}",
                'Fiyat': f"₺{txn.price:.2f}",
                'Komisyon': f"₺{txn.commission:.2f}",
                'Toplam': f"₺{txn.total_cost:,.2f}"
            })
        
        df = pd.DataFrame(transactions_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
