"""
Dashboard - Ana sayfa (kullanıcının portföyleri)
"""
import streamlit as st
from datetime import datetime

from src.auth.session import SessionManager
from src.db.repositories import PortfolioRepository, TransactionRepository
from src.db.models import Portfolio
from src.services.portfolio_calculator import PortfolioCalculator
from src.services.stock_data import get_stock_price


def show_dashboard():
    """Dashboard sayfasını göster"""
    user = SessionManager.get_current_user()
    if not user:
        st.error("Lütfen giriş yapın")
        st.session_state.page = 'login'
        st.rerun()
        return
    
    # Header
    st.title("📊 Portföylerim")
    st.markdown(f"Hoş geldin, **{user.email}** 👋")
    
    # Sidebar - Logout butonu
    with st.sidebar:
        st.markdown("---")
        if st.button("🚪 Çıkış Yap", use_container_width=True):
            SessionManager.logout()
    
    # Yeni portföy oluşturma
    with st.expander("➕ Yeni Portföy Oluştur", expanded=False):
        with st.form("new_portfolio_form"):
            portfolio_name = st.text_input(
                "Portföy Adı",
                placeholder="Örn: Teknoloji Portföyüm, Uzun Vadeli Yatırımlarım"
            )
            submit = st.form_submit_button("Oluştur", type="primary")
            
            if submit:
                if not portfolio_name:
                    st.error("Lütfen portföy adı girin")
                else:
                    portfolio_repo = PortfolioRepository()
                    new_portfolio = Portfolio(
                        portfolio_id='',
                        user_id=user.user_id,
                        name=portfolio_name,
                        created_at=datetime.now()
                    )
                    portfolio_id = portfolio_repo.create(new_portfolio)
                    st.success(f"✅ '{portfolio_name}' portföyü oluşturuldu!")
                    st.rerun()
    
    # Portföy listesi
    portfolio_repo = PortfolioRepository()
    transaction_repo = TransactionRepository()
    portfolios = portfolio_repo.get_by_user(user.user_id)
    
    if not portfolios:
        st.info("👆 Henüz portföyünüz yok. Yukarıdan yeni bir portföy oluşturun!")
        return
    
    st.markdown("---")
    st.subheader("Portföyleriniz")
    
    # Her portföy için kart
    for portfolio in portfolios:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.markdown(f"### 📁 {portfolio.name}")
                st.caption(f"Oluşturulma: {portfolio.created_at.strftime('%d.%m.%Y')}")
            
            # Portföy özetini hesapla
            transactions = transaction_repo.get_by_portfolio(portfolio.portfolio_id)
            positions = PortfolioCalculator.calculate_positions(transactions)
            
            if positions:
                summary = PortfolioCalculator.get_portfolio_summary(positions)
                
                with col2:
                    st.metric(
                        "Toplam Değer",
                        f"₺{summary['total_value']:,.2f}",
                        delta=f"₺{summary['total_profit_loss']:,.2f}",
                        delta_color="normal"
                    )
                
                with col3:
                    profit_color = "green" if summary['total_profit_loss'] >= 0 else "red"
                    st.markdown(f"**Kar/Zarar:** <span style='color:{profit_color}'>%{summary['total_profit_loss_percent']:.2f}</span>", unsafe_allow_html=True)
                    st.caption(f"{summary['positions_count']} pozisyon")
            else:
                with col2:
                    st.caption("Henüz işlem yok")
            
            with col4:
                if st.button("Aç →", key=f"open_{portfolio.portfolio_id}"):
                    st.session_state.page = 'portfolio'
                    st.session_state.current_portfolio_id = portfolio.portfolio_id
                    st.rerun()
            
            st.markdown("---")
