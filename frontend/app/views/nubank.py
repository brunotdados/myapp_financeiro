import pandas as pd
import streamlit as st

from services.finance_data import (
    add_category_pair,
    format_currency,
    get_next_numanomes,
    load_category_catalog,
    load_nubank_data,
    save_nubank_data,
    update_categorized_rows,
)


def render() -> None:
    df = load_nubank_data()
    target_numanomes = get_next_numanomes()

    st.markdown(
        f"""
        <div class="page-heading">
            <span>Banco Nubank</span>
            <h1>Cartao de Credito Nubank</h1>
            <p>Fatura a pagar, lancamentos do periodo e categorizacao dos gastos.</p>
            <div class="month-pill">Mes de pagamento: {target_numanomes}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df.empty:
        st.warning("Nenhum arquivo consolidado do Nubank foi encontrado.")
        return

    month_df = df[df["NUMANOMES"] == target_numanomes].copy()

    render_kpis(month_df=month_df, target_numanomes=target_numanomes)
    render_category_registration()
    render_month_table(full_df=df, month_df=month_df, target_numanomes=target_numanomes)


def render_kpis(month_df: pd.DataFrame, target_numanomes: str) -> None:
    totals_by_bank = month_df.groupby("banco")["valor"].sum().to_dict()
    total_month = float(month_df["valor"].sum()) if not month_df.empty else 0.0
    total_rows = len(month_df)

    banks = sorted(month_df["banco"].dropna().unique().tolist())
    while len(banks) < 2:
        banks.append("cartao pendente")

    st.markdown(
        f"""
        <div class="kpi-grid">
            {render_kpi_card(
                label=banks[0].title(),
                value=format_currency(float(totals_by_bank.get(banks[0], 0.0))),
                helper=f"Saldo para pagar em {target_numanomes}",
                color="#7c3aed",
            )}
            {render_kpi_card(
                label=banks[1].title(),
                value=format_currency(float(totals_by_bank.get(banks[1], 0.0))),
                helper=f"Saldo para pagar em {target_numanomes}",
                color="#2563eb",
            )}
            {render_kpi_card(
                label="Total dos cartoes",
                value=format_currency(total_month),
                helper=f"{total_rows} lancamentos no periodo",
                color="#15803d",
            )}
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


def render_category_registration() -> None:
    st.markdown(
        """
        <div class="section-card">
            <h2>Cadastro de categorias</h2>
            <p>Crie pares de categoria e subcategoria para classificar os lancamentos da fatura.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        col1, col2, col3 = st.columns([1, 1, 0.8])
        category = col1.text_input("Categoria", placeholder="Ex: Alimentacao")
        subcategory = col2.text_input("Subcategoria", placeholder="Ex: Mercado")

        with col3:
            st.write("")
            st.write("")
            submitted = st.button("Adicionar", use_container_width=True)

        if submitted:
            try:
                add_category_pair(category, subcategory)
                st.success("Categoria adicionada.")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))


def render_month_table(
    full_df: pd.DataFrame,
    month_df: pd.DataFrame,
    target_numanomes: str,
) -> None:
    st.markdown(
        f"""
        <div class="section-card">
            <h2>Lancamentos do mes</h2>
            <p>Classifique as compras do NUMANOMES {target_numanomes}. As alteracoes sao salvas na tabela consolidada.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if month_df.empty:
        st.info(f"Nenhum lancamento encontrado para NUMANOMES {target_numanomes}.")
        return

    catalog = load_category_catalog()
    category_options = [""] + sorted(catalog["categoria"].dropna().unique().tolist())
    subcategory_options = [""] + sorted(
        catalog["subcategoria"].dropna().unique().tolist()
    )

    editable_df = month_df.reset_index(names="_row_id")
    visible_columns = [
        "_row_id",
        "data_compra",
        "descricao",
        "valor",
        "banco",
        "categoria",
        "subcategoria",
    ]

    edited_df = st.data_editor(
        editable_df[visible_columns],
        hide_index=True,
        use_container_width=True,
        disabled=["_row_id", "data_compra", "descricao", "valor", "banco"],
        column_order=[
            "data_compra",
            "descricao",
            "valor",
            "banco",
            "categoria",
            "subcategoria",
        ],
        column_config={
            "data_compra": st.column_config.TextColumn("Data"),
            "descricao": st.column_config.TextColumn("Descricao", width="large"),
            "valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
            "banco": st.column_config.TextColumn("Cartao"),
            "categoria": st.column_config.SelectboxColumn(
                "Categoria",
                options=category_options,
            ),
            "subcategoria": st.column_config.SelectboxColumn(
                "Subcategoria",
                options=subcategory_options,
            ),
        },
        key=f"nubank_editor_{target_numanomes}",
    )

    col1, col2 = st.columns([0.28, 0.72])
    if col1.button("Salvar categorias", type="primary", use_container_width=True):
        updated_df = update_categorized_rows(full_df, edited_df)
        save_nubank_data(updated_df)
        st.success("Categorias salvas na tabela consolidada.")
        st.rerun()

    uncategorized = int(
        ((month_df["categoria"] == "") | (month_df["subcategoria"] == "")).sum()
    )
    col2.caption(f"{uncategorized} lancamentos ainda sem categoria ou subcategoria.")
