import pandas as pd
import streamlit as st

from services.finance_data import (
    TITHE_STATUS,
    format_currency,
    get_next_numanomes,
    load_monthly_tithe,
    save_monthly_tithe,
)


def render() -> None:
    df = load_monthly_tithe()
    target_numanomes = get_next_numanomes()

    st.markdown(
        f"""
        <div class="page-heading">
            <span>Dizimo mensal</span>
            <h1>Dizimo mensal</h1>
            <p>Controle mensal de 10% dos salarios de Bruno e Mayara.</p>
            <div class="month-pill">Mes de referencia: {target_numanomes}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_kpis(df=df, target_numanomes=target_numanomes)
    render_tithe_table(df=df)


def render_kpis(df: pd.DataFrame, target_numanomes: str) -> None:
    month_df = df[df["NUMANOMES"] == target_numanomes].copy()
    if month_df.empty:
        month_df = df.head(0)

    total_month = float(month_df["total_dizimo"].sum()) if not month_df.empty else 0.0
    bruno_month = float(month_df["dizimo_bruno"].sum()) if not month_df.empty else 0.0
    mayara_month = float(month_df["dizimo_mayara"].sum()) if not month_df.empty else 0.0

    st.markdown(
        f"""
        <div class="kpi-grid">
            {render_kpi_card("Bruno", format_currency(bruno_month), "10% de R$ 6.700,00", "#2563eb")}
            {render_kpi_card("Mayara", format_currency(mayara_month), "10% de R$ 5.600,00", "#7c3aed")}
            {render_kpi_card("Total do mes", format_currency(total_month), f"NUMANOMES {target_numanomes}", "#15803d")}
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


def render_tithe_table(df: pd.DataFrame) -> None:
    st.markdown(
        """
        <div class="section-card">
            <h2>Tabela anual</h2>
            <p>Os dizimos sao recalculados automaticamente como 10% dos salarios informados.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    edited_df = st.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        disabled=["id", "dizimo_bruno", "dizimo_mayara", "total_dizimo"],
        column_order=[
            "NUMANOMES",
            "salario_bruno",
            "dizimo_bruno",
            "salario_mayara",
            "dizimo_mayara",
            "total_dizimo",
            "status",
        ],
        column_config={
            "id": None,
            "NUMANOMES": st.column_config.TextColumn("NUMANOMES"),
            "salario_bruno": st.column_config.NumberColumn(
                "Salario Bruno",
                format="R$ %.2f",
            ),
            "dizimo_bruno": st.column_config.NumberColumn(
                "Dizimo Bruno",
                format="R$ %.2f",
            ),
            "salario_mayara": st.column_config.NumberColumn(
                "Salario Mayara",
                format="R$ %.2f",
            ),
            "dizimo_mayara": st.column_config.NumberColumn(
                "Dizimo Mayara",
                format="R$ %.2f",
            ),
            "total_dizimo": st.column_config.NumberColumn(
                "Total Dizimo",
                format="R$ %.2f",
            ),
            "status": st.column_config.SelectboxColumn(
                "Status",
                options=TITHE_STATUS,
            ),
        },
        key="monthly_tithe_editor",
    )

    col1, col2 = st.columns([0.28, 0.72])
    if col1.button("Salvar dizimos", type="primary", use_container_width=True):
        save_monthly_tithe(edited_df)
        st.success("Tabela de dizimo atualizada.")
        st.rerun()

    annual_total = float(df["total_dizimo"].sum()) if not df.empty else 0.0
    col2.caption(f"Total anual previsto: {format_currency(annual_total)}.")
