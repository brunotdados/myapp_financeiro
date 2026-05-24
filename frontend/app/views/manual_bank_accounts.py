import pandas as pd
import streamlit as st

from services.finance_data import (
    add_manual_bank_account,
    format_currency,
    get_next_numanomes,
    load_category_catalog,
    load_manual_bank_accounts,
    update_manual_bank_accounts,
)


def render() -> None:
    df = load_manual_bank_accounts()
    target_numanomes = get_next_numanomes()

    st.markdown(
        f"""
        <div class="page-heading">
            <span>Contas Banco</span>
            <h1>Adicionar contas banco</h1>
            <p>Cadastro manual de cartoes e bancos que nao possuem importacao automatica.</p>
            <div class="month-pill">Mes de pagamento: {target_numanomes}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_kpis(df=df, target_numanomes=target_numanomes)
    render_registration_form(default_numanomes=target_numanomes)
    render_accounts_table(df=df)


def render_kpis(df: pd.DataFrame, target_numanomes: str) -> None:
    month_df = df[df["NUMANOMES"] == target_numanomes].copy()
    total_month = float(month_df["valor"].sum()) if not month_df.empty else 0.0
    bank_count = int(month_df["banco"].nunique()) if not month_df.empty else 0
    row_count = len(month_df)

    highest_bank = "-"
    highest_value = 0.0
    if not month_df.empty:
        totals = month_df.groupby("banco")["valor"].sum().sort_values(ascending=False)
        highest_bank = totals.index[0].title()
        highest_value = float(totals.iloc[0])

    st.markdown(
        f"""
        <div class="kpi-grid">
            {render_kpi_card("Total manual", format_currency(total_month), f"NUMANOMES {target_numanomes}", "#2563eb")}
            {render_kpi_card("Bancos/cartoes", str(bank_count), f"{row_count} lancamentos cadastrados", "#7c3aed")}
            {render_kpi_card(highest_bank, format_currency(highest_value), "Maior saldo manual do mes", "#15803d")}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(label: str, value: str, helper: str, color: str) -> str:
    return f"""
    <div class="kpi-card" style="--card-color: {color};">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-helper">{helper}</div>
    </div>
    """


def render_registration_form(default_numanomes: str) -> None:
    st.markdown(
        """
        <div class="section-card">
            <h2>Cadastrar lancamento manual</h2>
            <p>Inclua compras de qualquer banco ou cartao, mantendo o mesmo formato da tabela Nubank.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    catalog = load_category_catalog()
    category_options = [""] + sorted(catalog["categoria"].dropna().unique().tolist())
    subcategory_options = [""] + sorted(
        catalog["subcategoria"].dropna().unique().tolist()
    )

    with st.form("manual_bank_account_form", clear_on_submit=True):
        purchase_date = st.date_input("Data da compra")
        numanomes = st.text_input("NUMANOMES", value=default_numanomes)
        bank = st.text_input("Banco/cartao", placeholder="Ex: santander")
        description = st.text_input("Descricao", placeholder="Ex: Supermercado")
        value = st.number_input("Valor", min_value=0.0, step=10.0, format="%.2f")
        category = st.selectbox("Categoria", category_options)
        subcategory = st.selectbox("Subcategoria", subcategory_options)

        submitted = st.form_submit_button(
            "Cadastrar lancamento",
            use_container_width=True,
        )

    if submitted:
        try:
            add_manual_bank_account(
                purchase_date=purchase_date,
                description=description,
                value=value,
                bank=bank,
                numanomes=numanomes,
                category=category,
                subcategory=subcategory,
            )
            st.success("Lancamento cadastrado.")
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))


def render_accounts_table(df: pd.DataFrame) -> None:
    st.markdown(
        """
        <div class="section-card">
            <h2>Tabela manual de bancos</h2>
            <p>Edite os lancamentos manuais de bancos e cartoes sempre que necessario.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df.empty:
        st.info("Nenhum lancamento manual cadastrado ainda.")
        return

    catalog = load_category_catalog()
    category_options = [""] + sorted(catalog["categoria"].dropna().unique().tolist())
    subcategory_options = [""] + sorted(
        catalog["subcategoria"].dropna().unique().tolist()
    )

    edited_df = st.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        disabled=["id", "origem"],
        column_order=[
            "data_compra",
            "descricao",
            "valor",
            "banco",
            "NUMANOMES",
            "categoria",
            "subcategoria",
        ],
        column_config={
            "id": None,
            "data_compra": st.column_config.TextColumn("Data"),
            "descricao": st.column_config.TextColumn("Descricao", width="large"),
            "valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
            "origem": st.column_config.TextColumn("Origem"),
            "NUMANOMES": st.column_config.TextColumn("NUMANOMES"),
            "banco": st.column_config.TextColumn("Banco/cartao"),
            "categoria": st.column_config.SelectboxColumn(
                "Categoria",
                options=category_options,
            ),
            "subcategoria": st.column_config.SelectboxColumn(
                "Subcategoria",
                options=subcategory_options,
            ),
        },
        key="manual_bank_accounts_editor",
    )

    col1, col2 = st.columns([0.28, 0.72])
    if col1.button("Salvar tabela", type="primary", use_container_width=True):
        update_manual_bank_accounts(edited_df)
        st.success("Lancamentos manuais atualizados.")
        st.rerun()

    col2.caption(f"{len(df)} lancamento(s) manual(is) cadastrado(s).")
