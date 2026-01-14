"""
Kullanıcı kaydı sayfası
"""
import streamlit as st
from src.auth.firebase_auth import AuthService
from src.auth.session import SessionManager


def show_register_page():
    """Kayıt sayfasını göster"""
    st.title("📝 Yeni Hesap Oluştur")
    st.markdown("BIST Portföy Takip Sistemi'ne hoş geldiniz!")
    
    with st.form("register_form"):
        email = st.text_input("Email", placeholder="ornek@email.com")
        password = st.text_input("Şifre", type="password", placeholder="En az 6 karakter")
        confirm_password = st.text_input("Şifre Tekrar", type="password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submit = st.form_submit_button("Kayıt Ol", use_container_width=True, type="primary")
        with col2:
            if st.form_submit_button("Giriş Sayfasına Dön", use_container_width=True):
                st.session_state.page = 'login'
                st.rerun()
        
        if submit:
            if not email or not password or not confirm_password:
                st.error("Lütfen tüm alanları doldurun")
            else:
                auth_service = AuthService()
                success, message, user = auth_service.register(email, password, confirm_password)
                
                if success:
                    st.success(message)
                    # Otomatik giriş yap
                    SessionManager.login(user)
                    st.session_state.page = 'dashboard'
                    st.rerun()
                else:
                    st.error(message)
    
    # Bilgilendirme
    with st.expander("ℹ️ Bilgi"):
        st.markdown("""
        **Kayıt Gereksinimleri:**
        - Geçerli bir email adresi
        - En az 6 karakter uzunluğunda şifre
        - Şifrelerin eşleşmesi gerekir
        
        Kayıt olduktan sonra otomatik olarak giriş yapılacak ve dashboard'a yönlendirileceksiniz.
        """)
