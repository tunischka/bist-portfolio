"""
BIST Portfolio SaaS - Ana Uygulama
Streamlit + Firebase ile çoklu kullanıcı portföy takip sistemi
"""
import streamlit as st
from src.auth.session import SessionManager
from src.ui.pages.login import show_login_page
from src.ui.pages.register import show_register_page
from src.ui.pages.dashboard import show_dashboard
from src.ui.pages.portfolio import show_portfolio_page


# Sayfa konfigürasyonu
st.set_page_config(
    page_title="BIST Portföy Takip",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Session state başlat
SessionManager.init_session()

# Sayfa yönlendirmesi
if 'page' not in st.session_state:
    st.session_state.page = 'login' if not SessionManager.is_logged_in() else 'dashboard'

# Ana routing mantığı
def main():
    """Ana uygulama"""
    
    # Giriş kontrolü
    if not SessionManager.is_logged_in():
        # Kullanıcı giriş yapmamış - Login veya Register
        if st.session_state.page == 'register':
            show_register_page()
        else:
            show_login_page()
    else:
        # Kullanıcı giriş yapmış - Dashboard veya Portfolio
        if st.session_state.page == 'portfolio':
            show_portfolio_page()
        else:
            show_dashboard()


if __name__ == "__main__":
    main()
