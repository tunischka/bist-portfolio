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
    
    # Yeni işlem ekleme - Modern UI
    st.subheader("➕ Yeni İşlem Ekle")
    
    from src.utils.bist_stocks import BIST_STOCKS, get_stock_display_name, search_stocks
    
    # Container for form
    with st.container():
        # Hisse seçimi (autocomplete)
        search_query = st.text_input(
            "🔍 Hisse Ara", 
            placeholder="THYAO, GARAN, İş Bankası...",
            key="stock_search",
            help="Hisse kodu veya şirket adı yazın"
        )
        
        filtered_stocks = search_stocks(search_query) if search_query else BIST_STOCKS
        
        if filtered_stocks:
            selected_symbol = st.selectbox(
                "Hisse Seç",
                options=list(filtered_stocks.keys()),
                format_func=lambda x: get_stock_display_name(x),
                key="stock_select"
            )
        else:
            st.warning("Arama sonucu bulunamadı")
            selected_symbol = None
        
        if selected_symbol:
            # Güncel fiyatı çek
            current_price = get_stock_price(selected_symbol)
            if current_price is None or current_price == 0:
                current_price = 100.0  # Default
                st.warning(f"⚠️ {selected_symbol} için güncel fiyat alınamadı. Manuel fiyat girin.")
            
            # Fiyat kontrolü
            st.markdown("### 💰 Fiyat")
            col1, col2, col3, col4, col5 = st.columns([3, 0.7, 0.7, 0.7, 0.7])
            
            with col1:
                if 'transaction_price' not in st.session_state:
                    st.session_state.transaction_price = current_price
                
                price = st.number_input(
                    "Birim Fiyat (₺)",
                    min_value=0.01,
                    value=float(st.session_state.transaction_price),
                    step=0.01,
                    format="%.2f",
                    key="price_input",
                    label_visibility="collapsed"
                )
                st.session_state.transaction_price = price
            
            with col2:
                if st.button("−10", use_container_width=True, key="minus_10"):
                    st.session_state.transaction_price = max(0.01, price - 10)
                    st.rerun()
            with col3:
                if st.button("−1", use_container_width=True, key="minus_1"):
                    st.session_state.transaction_price = max(0.01, price - 1)
                    st.rerun()
            with col4:
                if st.button("+1", use_container_width=True, key="plus_1"):
                    st.session_state.transaction_price = price + 1
                    st.rerun()
            with col5:
                if st.button("+10", use_container_width=True, key="plus_10"):
                    st.session_state.transaction_price = price + 10
                    st.rerun()
            
            # Adet girişi
            st.markdown("### 📦 Adet")
            quantity = st.number_input(
                "Miktar",
                min_value=1.0,
                value=1.0,
                step=1.0,
                key="quantity_input",
                label_visibility="collapsed"
            )
            
            # Toplam tutar
            total = price * quantity
            st.metric("💵 Toplam", f"₺{total:,.2f}")
            
            st.markdown("---")
            
            # Buy/Sell butonları
            col1, col2 = st.columns(2)
            with col1:
                buy_clicked = st.button(
                    "🟢 AL",
                    use_container_width=True,
                    type="primary",
                    key="buy_btn"
                )
            with col2:
                sell_clicked = st.button(
                    "🔴 SAT",
                    use_container_width=True,
                    key="sell_btn"
                )
            
            # Advanced mode toggle
            st.markdown("---")
            show_advanced = st.checkbox("⚙️ Gelişmiş Seçenekler", value=False, key="adv_toggle")
            
            if show_advanced:
                col1, col2 = st.columns(2)
                with col1:
                    transaction_date = st.date_input(
                        "📅 İşlem Tarihi",
                        value=datetime.now(),
                        key="adv_date"
                    )
                with col2:
                    commission = st.number_input(
                        "💳 Komisyon (₺)",
                        min_value=0.0,
                        value=0.0,
                        step=0.01,
                        format="%.2f",
                        key="adv_commission"
                    )
            else:
                transaction_date = datetime.now()
                commission = 0.0
            
            # İşlem kaydı
            if buy_clicked or sell_clicked:
                transaction_type = "BUY" if buy_clicked else "SELL"
                
                new_transaction = Transaction(
                    transaction_id='',
                    portfolio_id=portfolio_id,
                    symbol=selected_symbol if selected_symbol.endswith('.IS') else f"{selected_symbol}.IS",
                    transaction_type=transaction_type,
                    quantity=quantity,
                    price=price,
                    commission=commission,
                    transaction_date=datetime.combine(transaction_date, datetime.min.time()),
                    created_at=datetime.now()
                )
                
                transaction_repo.create(new_transaction)
                st.success(f"✅ {transaction_type} işlemi kaydedildi: {quantity} adet {selected_symbol} @ ₺{price}")
                
                # Reset price
                st.session_state.transaction_price = current_price
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
