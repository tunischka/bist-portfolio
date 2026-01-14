"""
Streamlit session state ile kullanıcı oturum yönetimi
"""
import streamlit as st
from typing import Optional
from ..db.models import User


class SessionManager:
    """Session state yöneticisi"""
    
    @staticmethod
    def init_session():
        """Session state'i başlat"""
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'user_id' not in st.session_state:
            st.session_state.user_id = None
        if 'email' not in st.session_state:
            st.session_state.email = None
    
    @staticmethod
    def is_logged_in() -> bool:
        """Kullanıcı giriş yapmış mı?"""
        SessionManager.init_session()
        return st.session_state.user is not None and st.session_state.user_id is not None
    
    @staticmethod
    def login(user: User):
        """Kullanıcı girişi yap"""
        st.session_state.user = user
        st.session_state.user_id = user.user_id
        st.session_state.email = user.email
    
    @staticmethod
    def logout():
        """Çıkış yap"""
        st.session_state.user = None
        st.session_state.user_id = None
        st.session_state.email = None
        st.rerun()
    
    @staticmethod
    def get_current_user() -> Optional[User]:
        """Mevcut kullanıcıyı al"""
        SessionManager.init_session()
        return st.session_state.user
    
    @staticmethod
    def get_current_user_id() -> Optional[str]:
        """Mevcut kullanıcı ID'sini al"""
        SessionManager.init_session()
        return st.session_state.user_id
