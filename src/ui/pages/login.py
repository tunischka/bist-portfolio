"""
Kullanıcı giriş sayfası
"""
import streamlit as st
from src.auth.firebase_auth import AuthService
from src.auth.session import SessionManager


def show_login_page():
    """Giriş sayfasını göster"""
    st.title("🔐 Giriş Yap")
    st.markdown("BIST Portföy Takip Sistemi")
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="ornek@email.com")
        password = st.text_input("Şifre", type="password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submit = st.form_submit_button("Giriş Yap", use_container_width=True, type="primary")
        with col2:
            if st.form_submit_button("Hesap Oluştur", use_container_width=True):
                st.session_state.page = 'register'
                st.rerun()
        
        if submit:
            if not email or not password:
                st.error("Lütfen email ve şifrenizi girin")
            else:
                auth_service = AuthService()
                success, message, user = auth_service.login(email, password)
                
                if success:
                    st.success(message)
                    SessionManager.login(user)
                    st.session_state.page = 'dashboard'
                    st.rerun()
                else:
                    st.error(message)
    
    # Bilgilendirme
    st.info("⚠️ **Not:** Bu demo bir uygulamadır. Gerçek bir uygulama için güvenli şifre hash'leme kullanılmalıdır.")
