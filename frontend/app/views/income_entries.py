import pandas as pd
import streamlit as st

from services.finance_data import (
    INCOME_STATUS,
    add_income_entry,
    format_currency,
    get_next_numanomes,
    load_income_entries,
    update_income_entries,
)


def render() -> None:
    df = load_income_entries()
    default_numanomes = get_next_numanomes()

    st.markdown(
        """
        <div class="page-heading">
            <span>Entradas</span>
            <h1>Entradas de salarios e outros</h1>
            <p>Cadastro mensal das receitas previstas e recebidas.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_kpis(df=df, default_numanomes=default_numanomes)
    render_registration_form(default_numanomes=default_numanomes)
    render_entries_table(df=df)


def render_kpis(df: pd.DataFrame, default_numanomes: str) -> None:
    month_df = df[df["NUMANOMES"] == default_numanomes].copy()
    total_month = float(month_df["valor"].sum()) if not month_df.empty else 0.0
    received = float(month_df.loc[month_df["status"] == "Recebido", "valor"].sum())
    expected = float(month_df.loc[month_df["status"] == "Previsto", "valor"].sum())

    st.markdown(
        f"""
        <div class="kpi-grid">
            {render_kpi_card("Total previsto", format_currency(total_month), f"NUMANOMES {default_numanomes}", "#2563eb")}
            {render_kpi_card("Recebido", format_currency(received), "Entradas confirmadas", "#15803d")}
            {render_kpi_card("A receber", format_currency(expected), "Entradas ainda previstas", "#b54708")}
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
            <h2>Cadastrar entrada</h2>
            <p>Adicione salarios, rendas extras, reembolsos ou outras entradas do mes.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("income_entry_form", clear_on_submit=True):
        col1, col2 = st.columns([0.35, 0.65])
        numanomes = col1.text_input("NUMANOMES", value=default_numanomes)
        description = col2.text_input("Descricao da entrada", placeholder="Ex: Salario")

        col3, col4 = st.columns([0.35, 0.65])
        value = col3.number_input("Valor", min_value=0.0, step=100.0, format="%.2f")
        status = col4.selectbox("Status", INCOME_STATUS)

        submitted = st.form_submit_button("Cadastrar entrada", use_container_width=True)

    if submitted:
        try:
            add_income_entry(
                numanomes=numanomes,
                description=description,
                value=value,
                status=status,
            )
            st.success("Entrada cadastrada.")
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))


def render_entries_table(df: pd.DataFrame) -> None:
    st.markdown(
        """
        <div class="section-card">
            <h2>Tabela de entradas</h2>
            <p>Edite valores, descricao, mes de pagamento e status sempre que necessario.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df.empty:
        st.info("Nenhuma entrada cadastrada ainda.")
        return

    edited_df = st.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        disabled=["id"],
        column_order=["NUMANOMES", "descricao", "valor", "status"],
        column_config={
            "id": None,
            "NUMANOMES": st.column_config.TextColumn("NUMANOMES"),
            "descricao": st.column_config.TextColumn("Descricao", width="large"),
            "valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
            "status": st.column_config.SelectboxColumn(
                "Status",
                options=INCOME_STATUS,
            ),
        },
        key="income_entries_editor",
    )

    col1, col2 = st.columns([0.28, 0.72])
    if col1.button("Salvar tabela", type="primary", use_container_width=True):
        update_income_entries(edited_df)
        st.success("Entradas atualizadas.")
        st.rerun()

    expected_count = int((df["status"] == "Previsto").sum())
    col2.caption(f"{expected_count} entrada(s) prevista(s) na tabela.")
