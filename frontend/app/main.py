import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from components.auth import login_form
from services.storage import get_secret
from styles.theme import apply_theme
from views import (
    dashboard,
    house_bills,
    income_entries,
    manual_bank_accounts,
    monthly_tithe,
    nubank,
)


NAV_ITEMS = {
    "Dashboard": lambda: dashboard.render(),
    "Contas Casa": lambda: house_bills.render(),
    "Entradas de Salarios e Outros": lambda: income_entries.render(),
    "Dizimo Mensal": lambda: monthly_tithe.render(),
    "Banco Nubank": lambda: nubank.render(),
    "Adicionar Contas Banco": lambda: manual_bank_accounts.render(),
}


def main() -> None:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    st.set_page_config(
        page_title="Controle Financeiro Pessoal",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "active_page" not in st.session_state:
        st.session_state.active_page = "Dashboard"

    apply_theme(authenticated=st.session_state.authenticated)

    if not st.session_state.authenticated:
        login_form(
            expected_user=get_secret("FINANCE_APP_USER") or os.getenv("FINANCE_APP_USER", "admin"),
            expected_password=get_secret("FINANCE_APP_PASSWORD") or os.getenv("FINANCE_APP_PASSWORD", "admin"),
        )
        return

    render_authenticated_home()


def render_authenticated_home() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <strong>Controle Financeiro</strong>
                <span>Painel pessoal</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        selected_page = st.radio(
            "Navegacao",
            list(NAV_ITEMS.keys()),
            index=list(NAV_ITEMS.keys()).index(st.session_state.active_page),
            label_visibility="collapsed",
        )
        st.session_state.active_page = selected_page

        st.divider()
        if st.button("Sair", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.pop("username", None)
            st.session_state.active_page = "Dashboard"
            st.rerun()

    username = st.session_state.get("username", "usuario")
    st.markdown(
        f"""
        <div class="topbar">
            <div>
                <span>Bem-vindo</span>
                <strong>{username}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    NAV_ITEMS[st.session_state.active_page]()


if __name__ == "__main__":
    main()
