import hmac

import streamlit as st


def login_form(expected_user: str, expected_password: str) -> None:
    st.markdown(
        """
        <div class="login-copy">
            <h1>Financas - Perroni & Toselli</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Usuario", autocomplete="username")
            password = st.text_input(
                "Senha",
                type="password",
                autocomplete="current-password",
            )
            submitted = st.form_submit_button("Entrar", use_container_width=True)

        if submitted:
            if _check_credentials(username, password, expected_user, expected_password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()

            st.error("Usuario ou senha invalidos.")


def logout_button() -> None:
    if st.button("Sair", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.pop("username", None)
        st.rerun()


def _check_credentials(
    username: str,
    password: str,
    expected_user: str,
    expected_password: str,
) -> bool:
    user_ok = hmac.compare_digest(username.strip(), expected_user)
    password_ok = hmac.compare_digest(password, expected_password)
    return user_ok and password_ok
