import streamlit as st


def apply_theme(authenticated: bool) -> None:
    sidebar_visibility = "block" if authenticated else "none"
    block_width = "1120px" if authenticated else "460px"
    block_padding = "32px 32px 40px" if authenticated else "11vh 18px 32px"

    css = """
        <style>
        :root {
            --finance-bg: #f7f8fa;
            --finance-panel: #ffffff;
            --finance-border: #d9dee8;
            --finance-text: #1f2937;
            --finance-muted: #667085;
            --finance-accent: #2563eb;
            --finance-accent-dark: #1d4ed8;
            --finance-green: #15803d;
            --finance-red: #b42318;
            --finance-yellow: #b54708;
        }

        .stApp {
            background: var(--finance-bg);
            color: var(--finance-text);
        }

        [data-testid="stSidebar"] {
            display: __SIDEBAR_VISIBILITY__;
        }

        [data-testid="stHeader"] {
            background: transparent;
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
            margin-bottom: 24px;
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
            font-size: 34px;
            line-height: 1.12;
            margin: 8px 0 10px;
            letter-spacing: 0;
        }

        .login-copy p,
        .page-heading p {
            color: var(--finance-muted);
            font-size: 16px;
            line-height: 1.55;
            margin: 0;
        }

        .stButton > button,
        .stFormSubmitButton > button {
            border-radius: 6px;
            border-color: var(--finance-accent);
            background: var(--finance-accent);
            color: white;
            min-height: 42px;
            font-weight: 600;
        }

        .stButton > button:hover,
        .stFormSubmitButton > button:hover {
            border-color: var(--finance-accent-dark);
            background: var(--finance-accent-dark);
            color: white;
        }

        .stTextInput input {
            border-radius: 6px;
            min-height: 42px;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 8px;
        }

        .sidebar-brand {
            padding: 10px 4px 22px;
        }

        .sidebar-brand strong {
            display: block;
            color: #f9fafb;
            font-size: 20px;
            letter-spacing: 0;
        }

        .sidebar-brand span {
            color: #cbd5e1;
            font-size: 13px;
        }

        [data-testid="stSidebar"] {
            background: #0f172a;
        }

        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span {
            color: #dbe4f0;
        }

        [data-testid="stSidebar"] [role="radiogroup"] {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        [data-testid="stSidebar"] [data-testid="stRadio"] label {
            background: transparent;
            border-radius: 8px;
            padding: 8px 10px;
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
            margin-bottom: 18px;
        }

        .topbar > div {
            background: var(--finance-panel);
            border: 1px solid var(--finance-border);
            border-radius: 8px;
            padding: 10px 14px;
            min-width: 180px;
            box-shadow: 0 8px 24px rgba(31, 41, 55, 0.06);
        }

        .topbar strong {
            display: block;
            color: var(--finance-text);
            font-size: 16px;
            margin-top: 2px;
        }

        .page-heading {
            margin-bottom: 24px;
        }

        .page-heading h1 {
            color: var(--finance-text);
            font-size: 38px;
            letter-spacing: 0;
            line-height: 1.15;
            margin: 6px 0 8px;
        }

        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 16px;
            margin: 16px 0 26px;
        }

        .kpi-card,
        .section-card {
            background: var(--finance-panel);
            border: 1px solid var(--finance-border);
            border-radius: 8px;
            box-shadow: 0 10px 28px rgba(31, 41, 55, 0.07);
        }

        .kpi-card {
            padding: 18px;
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
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 0;
            text-transform: uppercase;
        }

        .kpi-value {
            color: var(--finance-text);
            font-size: 30px;
            font-weight: 800;
            line-height: 1.15;
            margin-top: 10px;
        }

        .kpi-helper {
            color: var(--finance-muted);
            font-size: 14px;
            margin-top: 8px;
        }

        .section-card {
            padding: 22px;
            margin-top: 18px;
        }

        .section-card h2 {
            color: var(--finance-text);
            font-size: 22px;
            margin: 0 0 6px;
            letter-spacing: 0;
        }

        .section-card p {
            color: var(--finance-muted);
            margin: 0 0 16px;
        }

        .month-pill {
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            background: #eff6ff;
            color: var(--finance-accent-dark);
            font-weight: 700;
            padding: 6px 10px;
            margin-top: 14px;
            font-size: 13px;
        }

        @media (max-width: 640px) {
            .block-container {
                max-width: 100%;
                padding: 24px 14px 28px;
            }

            [data-testid="stVerticalBlockBorderWrapper"] {
                padding: 22px 16px 18px;
            }

            .login-copy h1,
            .page-heading h1 {
                font-size: 28px;
            }

            .kpi-grid {
                grid-template-columns: 1fr;
            }

            .kpi-value {
                font-size: 26px;
            }

            .topbar {
                justify-content: stretch;
            }

            .topbar > div {
                width: 100%;
            }
        }
        </style>
        """
    css = (
        css.replace("__SIDEBAR_VISIBILITY__", sidebar_visibility)
        .replace("__BLOCK_WIDTH__", block_width)
        .replace("__BLOCK_PADDING__", block_padding)
    )

    st.markdown(
        css,
        unsafe_allow_html=True,
    )
