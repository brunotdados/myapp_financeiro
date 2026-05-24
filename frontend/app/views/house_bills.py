import pandas as pd
import streamlit as st

from services.finance_data import (
    HOUSE_BILL_STATUS,
    add_house_bill,
    format_currency,
    get_next_numanomes,
    load_house_bills,
    update_house_bills,
)


def render() -> None:
    df = load_house_bills()
    default_numanomes = get_next_numanomes()

    st.markdown(
        """
        <div class="page-heading">
            <span>Contas Casa</span>
            <h1>Contas da casa</h1>
            <p>Cadastro mensal das contas, valores e status de pagamento.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_kpis(df=df, default_numanomes=default_numanomes)
    render_registration_form(default_numanomes=default_numanomes)
    render_bills_table(df=df)


def render_kpis(df: pd.DataFrame, default_numanomes: str) -> None:
    month_df = df[df["NUMANOMES"] == default_numanomes].copy()
    total_month = float(month_df["valor"].sum()) if not month_df.empty else 0.0
    paid = float(month_df.loc[month_df["status"] == "Pago", "valor"].sum())
    pending = float(month_df.loc[month_df["status"] == "Pendente", "valor"].sum())

    st.markdown(
        f"""
        <div class="kpi-grid">
            {render_kpi_card("Total do mes", format_currency(total_month), f"NUMANOMES {default_numanomes}", "#2563eb")}
            {render_kpi_card("Pago", format_currency(paid), "Contas ja quitadas", "#15803d")}
            {render_kpi_card("Pendente", format_currency(pending), "Saldo ainda em aberto", "#b54708")}
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
            <h2>Cadastrar conta</h2>
            <p>Adicione manualmente as contas da casa para o mes de pagamento.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("house_bill_form", clear_on_submit=True):
        numanomes = st.text_input("NUMANOMES", value=default_numanomes)
        description = st.text_input("Descricao da conta", placeholder="Ex: Energia")
        value = st.number_input("Valor", min_value=0.0, step=10.0, format="%.2f")
        status = st.selectbox("Status", HOUSE_BILL_STATUS)

        submitted = st.form_submit_button("Cadastrar conta", use_container_width=True)

    if submitted:
        try:
            add_house_bill(
                numanomes=numanomes,
                description=description,
                value=value,
                status=status,
            )
            st.success("Conta cadastrada.")
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))


def render_bills_table(df: pd.DataFrame) -> None:
    st.markdown(
        """
        <div class="section-card">
            <h2>Tabela de contas</h2>
            <p>Edite valores, descricao, mes de pagamento e status sempre que necessario.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df.empty:
        st.info("Nenhuma conta cadastrada ainda.")
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
                options=HOUSE_BILL_STATUS,
            ),
        },
        key="house_bills_editor",
    )

    col1, col2 = st.columns([0.28, 0.72])
    if col1.button("Salvar tabela", type="primary", use_container_width=True):
        update_house_bills(edited_df)
        st.success("Contas atualizadas.")
        st.rerun()

    pending_count = int((df["status"] == "Pendente").sum())
    col2.caption(f"{pending_count} conta(s) pendente(s) na tabela.")
