import streamlit as st


def apply_theme(authenticated: bool) -> None:
    sidebar_visibility = "block" if authenticated else "none"
    block_width = "1040px" if authenticated else "420px"
    block_padding = "20px 20px 28px" if authenticated else "9vh 18px 24px"

    css = """
        <style>
        :root {
            --finance-bg: #000000;
            --finance-panel: #0b0b0f;
            --finance-panel-soft: #111118;
            --finance-border: #2a2a33;
            --finance-text: #f9fafb;
            --finance-muted: #a1a1aa;
            --finance-accent: #ffffff;
            --finance-accent-dark: #d4d4d8;
            --finance-green: #22c55e;
            --finance-red: #ef4444;
            --finance-yellow: #f59e0b;
        }

        .stApp {
            background: var(--finance-bg);
            color: var(--finance-text);
        }

        [data-testid="stSidebar"] {
            display: __SIDEBAR_VISIBILITY__;
        }

        [data-testid="stHeader"] {
            background: #000000;
        }

        #MainMenu,
        footer {
            visibility: hidden;
        }

        .block-container {
            max-width: __BLOCK_WIDTH__;
            padding: __BLOCK_PADDING__;
        }

        .login-copy {
            text-align: center;
            margin-bottom: 32px;
        }

        .login-copy span,
        .page-heading span,
        .topbar span {
            color: var(--finance-accent);
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 0;
            text-transform: uppercase;
        }

        .login-copy h1 {
            color: var(--finance-text);
            font-size: 38px;
            line-height: 1.12;
            margin: 0;
            letter-spacing: 0;
        }

        .login-copy p,
        .page-heading p {
            color: var(--finance-muted);
            font-size: 14px;
            line-height: 1.45;
            margin: 0;
        }

        .stButton > button,
        .stFormSubmitButton > button {
            border-radius: 6px;
            border-color: var(--finance-accent);
            background: var(--finance-accent);
            color: #000000;
            min-height: 38px;
            font-weight: 600;
        }

        .stButton > button:hover,
        .stFormSubmitButton > button:hover {
            border-color: var(--finance-accent-dark);
            background: var(--finance-accent-dark);
            color: #000000;
        }

        .stTextInput input {
            border-radius: 6px;
            min-height: 38px;
            background: #ffffff;
            border: 1px solid #d1d5db;
            color: #111827;
        }

        .stTextInput label {
            color: var(--finance-text);
            font-weight: 700;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 8px;
            background: var(--finance-panel);
            border: 1px solid var(--finance-border);
        }

        [data-baseweb="select"] > div,
        [data-baseweb="input"] > div,
        [data-baseweb="base-input"],
        textarea,
        input {
            background: #ffffff;
            color: #111827;
        }

        [data-testid="stDataFrame"],
        [data-testid="stDataEditor"] {
            border: 1px solid var(--finance-border);
            border-radius: 8px;
            overflow: hidden;
        }

        .stAlert {
            background: var(--finance-panel-soft);
            color: var(--finance-text);
        }

        .sidebar-brand {
            padding: 4px 4px 14px;
        }

        .sidebar-brand strong {
            display: block;
            color: #f9fafb;
            font-size: 18px;
            letter-spacing: 0;
        }

        .sidebar-brand span {
            color: #cbd5e1;
            font-size: 13px;
        }

        [data-testid="stSidebar"] {
            background: #000000;
            border-right: 1px solid var(--finance-border);
        }

        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span {
            color: #dbe4f0;
        }

        [data-testid="stSidebar"] [role="radiogroup"] {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label {
            background: transparent;
            border-radius: 8px;
            padding: 6px 8px;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
            background: rgba(255, 255, 255, 0.08);
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
            background: rgba(37, 99, 235, 0.22);
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) span {
            color: #ffffff;
            font-weight: 700;
        }

        .topbar {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 10px;
        }

        .topbar > div {
            background: var(--finance-panel);
            border: 1px solid var(--finance-border);
            border-radius: 8px;
            padding: 8px 12px;
            min-width: 180px;
            box-shadow: none;
        }

        .topbar strong {
            display: block;
            color: var(--finance-text);
            font-size: 14px;
            margin-top: 2px;
        }

        .page-heading {
            margin-bottom: 14px;
        }

        .page-heading h1 {
            color: var(--finance-text);
            font-size: 30px;
            letter-spacing: 0;
            line-height: 1.15;
            margin: 6px 0 8px;
        }

        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 10px;
            margin: 10px 0 16px;
        }

        .kpi-card,
        .section-card {
            background: var(--finance-panel);
            border: 1px solid var(--finance-border);
            border-radius: 8px;
            box-shadow: none;
        }

        .kpi-card {
            padding: 13px;
            position: relative;
            overflow: hidden;
        }

        .kpi-card::before {
            content: "";
            display: block;
            height: 4px;
            background: var(--card-color);
            position: absolute;
            left: 0;
            top: 0;
            right: 0;
        }

        .kpi-label {
            color: var(--finance-muted);
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0;
            text-transform: uppercase;
        }

        .kpi-value {
            color: var(--finance-text);
            font-size: 24px;
            font-weight: 800;
            line-height: 1.15;
            margin-top: 7px;
        }

        .kpi-helper {
            color: var(--finance-muted);
            font-size: 12px;
            margin-top: 6px;
        }

        .section-card {
            padding: 14px;
            margin-top: 12px;
        }

        .section-card h2 {
            color: var(--finance-text);
            font-size: 18px;
            margin: 0 0 6px;
            letter-spacing: 0;
        }

        .section-card p {
            color: var(--finance-muted);
            margin: 0 0 10px;
        }

        .month-pill {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            background: #ffffff;
            color: #000000;
            font-weight: 700;
            padding: 5px 8px;
            margin-top: 10px;
            font-size: 12px;
        }

        div[data-testid="stVerticalBlock"] {
            gap: 0.7rem;
        }

        div[data-testid="stHorizontalBlock"] {
            gap: 0.7rem;
        }

        @media (max-width: 640px) {
            .block-container {
                max-width: 100%;
                padding: 10px 10px 18px;
            }

            [data-testid="stVerticalBlockBorderWrapper"] {
                padding: 12px 10px;
            }

            .login-copy h1,
            .page-heading h1 {
                font-size: 22px;
            }

            .kpi-grid {
                grid-template-columns: 1fr;
                gap: 8px;
                margin: 8px 0 12px;
            }

            .kpi-value {
                font-size: 21px;
            }

            .kpi-card {
                padding: 11px 12px;
            }

            .kpi-helper {
                display: none;
            }

            .page-heading {
                margin-bottom: 10px;
            }

            .page-heading p {
                font-size: 13px;
            }

            .section-card {
                padding: 11px;
                margin-top: 10px;
            }

            .section-card h2 {
                font-size: 16px;
            }

            .section-card p {
                display: none;
            }

            .month-pill {
                font-size: 11px;
                padding: 4px 7px;
                margin-top: 7px;
            }

            .stButton > button,
            .stFormSubmitButton > button,
            .stTextInput input {
                min-height: 34px;
            }

            [data-testid="stSidebar"] [data-testid="stRadio"] label {
                padding: 5px 7px;
            }

            .sidebar-brand strong {
                font-size: 16px;
            }

            .sidebar-brand span {
                display: none;
            }

            .topbar {
                display: none;
            }

            div[data-testid="stDataFrame"],
            div[data-testid="stDataEditor"] {
                max-height: 360px;
            }
        }

        __LOGIN_CSS__
        </style>
        """
    css = (
        css.replace("__SIDEBAR_VISIBILITY__", sidebar_visibility)
        .replace("__BLOCK_WIDTH__", block_width)
        .replace("__BLOCK_PADDING__", block_padding)
        .replace("__LOGIN_CSS__", build_login_css(authenticated))
    )

    st.markdown(
        css,
        unsafe_allow_html=True,
    )


def build_login_css(authenticated: bool) -> str:
    if authenticated:
        return ""

    return """
        [data-testid="stHeader"] {
            display: none;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            background: transparent;
            border: 0;
            box-shadow: none;
            padding: 0;
        }

        .stTextInput input {
            background: #ffffff;
            border: 1px solid #d1d5db;
            color: #111827;
        }

        .stTextInput input:focus {
            border-color: #ffffff;
            box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.22);
        }

        .stFormSubmitButton > button {
            background: #ffffff;
            border-color: #ffffff;
            color: #000000;
        }

        .stFormSubmitButton > button:hover {
            background: #e5e7eb;
            border-color: #e5e7eb;
            color: #000000;
        }
    """
