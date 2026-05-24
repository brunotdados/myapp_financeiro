import pandas as pd
import streamlit as st

from services.finance_data import (
    format_currency,
    get_next_numanomes,
    load_house_bills,
    load_income_entries,
    load_manual_bank_accounts,
    load_monthly_tithe,
    load_nubank_data,
)


def render() -> None:
    data = load_dashboard_data()
    selected_numanomes = render_filters(data)
    month_data = filter_month_data(data, selected_numanomes)
    totals = calculate_month_totals(month_data)

    st.markdown(
        f"""
        <div class="page-heading">
            <span>Dashboard</span>
            <h1>Resumo financeiro</h1>
            <p>Visao consolidada de entradas, contas, cartoes, dizimo e saldo mensal.</p>
            <div class="month-pill">NUMANOMES selecionado: {selected_numanomes}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_kpis(totals)
    render_charts(month_data, data)
    render_house_bills_table(month_data["house_bills"], selected_numanomes)


def load_dashboard_data() -> dict[str, pd.DataFrame]:
    return {
        "income": load_income_entries(),
        "house_bills": load_house_bills(),
        "nubank": load_nubank_data(),
        "manual_banks": load_manual_bank_accounts(),
        "tithe": load_monthly_tithe(),
    }


def render_filters(data: dict[str, pd.DataFrame]) -> str:
    options = collect_numanomes_options(data)

    with st.container(border=True):
        col1, col2 = st.columns([0.35, 0.65])
        selected = col1.selectbox(
            "Filtrar por NUMANOMES",
            options,
            index=options.index(get_next_numanomes())
            if get_next_numanomes() in options
            else 0,
        )
        col2.caption("Use este filtro para comparar o mes de pagamento no painel.")

    return selected


def collect_numanomes_options(data: dict[str, pd.DataFrame]) -> list[str]:
    values: set[str] = {get_next_numanomes()}

    for df in data.values():
        if not df.empty and "NUMANOMES" in df.columns:
            values.update(df["NUMANOMES"].dropna().astype(str).tolist())

    return sorted(values, reverse=True)


def filter_month_data(
    data: dict[str, pd.DataFrame],
    selected_numanomes: str,
) -> dict[str, pd.DataFrame]:
    return {
        key: filter_by_numanomes(df, selected_numanomes)
        for key, df in data.items()
    }


def filter_by_numanomes(df: pd.DataFrame, selected_numanomes: str) -> pd.DataFrame:
    if df.empty or "NUMANOMES" not in df.columns:
        return df.head(0).copy()

    return df[df["NUMANOMES"].astype(str) == selected_numanomes].copy()


def calculate_month_totals(month_data: dict[str, pd.DataFrame]) -> dict[str, float]:
    total_income = sum_column(month_data["income"], "valor")
    total_house_bills = sum_column(month_data["house_bills"], "valor")
    total_nubank = sum_column(month_data["nubank"], "valor")
    total_manual_banks = sum_column(month_data["manual_banks"], "valor")
    total_bank_accounts = total_nubank + total_manual_banks
    total_tithe = sum_column(month_data["tithe"], "total_dizimo")
    balance = total_income - total_house_bills - total_bank_accounts - total_tithe

    return {
        "income": total_income,
        "house_bills": total_house_bills,
        "bank_accounts": total_bank_accounts,
        "tithe": total_tithe,
        "balance": balance,
    }


def sum_column(df: pd.DataFrame, column: str) -> float:
    if df.empty or column not in df.columns:
        return 0.0

    return float(pd.to_numeric(df[column], errors="coerce").fillna(0.0).sum())


def render_kpis(totals: dict[str, float]) -> None:
    balance_color = "#15803d" if totals["balance"] >= 0 else "#b42318"
    st.markdown(
        f"""
        <div class="kpi-grid">
            {render_kpi_card("Total de entradas", format_currency(totals["income"]), "Receitas cadastradas no mes", "#15803d")}
            {render_kpi_card("Contas da casa", format_currency(totals["house_bills"]), "Despesas fixas e manuais", "#b54708")}
            {render_kpi_card("Cartoes e bancos", format_currency(totals["bank_accounts"]), "Nubank + contas adicionadas", "#2563eb")}
            {render_kpi_card("Dizimo", format_currency(totals["tithe"]), "Dizimo mensal previsto", "#7c3aed")}
            {render_kpi_card("Saldo", format_currency(totals["balance"]), "Entradas - contas - dizimo", balance_color)}
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


def render_charts(
    month_data: dict[str, pd.DataFrame],
    full_data: dict[str, pd.DataFrame],
) -> None:
    st.markdown(
        """
        <div class="section-card">
            <h2>Analises do mes</h2>
            <p>Distribuicao por categoria, bancos/cartoes e contas da casa.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    category_df = build_category_chart_data(month_data)
    bank_df = build_bank_chart_data(month_data)
    house_df = build_house_bills_chart_data(month_data["house_bills"])

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Categorias")
        render_bar_chart_or_empty(category_df, "valor", "Sem categorias no mes.")

    with col2:
        st.subheader("Bancos e cartoes")
        render_bar_chart_or_empty(bank_df, "valor", "Sem bancos/cartoes no mes.")

    st.subheader("Contas da casa")
    render_bar_chart_or_empty(house_df, "valor", "Sem contas da casa no mes.")

    st.markdown(
        """
        <div class="section-card">
            <h2>Historico mensal</h2>
            <p>Comparativo de entradas, despesas, dizimo e saldo por NUMANOMES.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    history_df = build_monthly_history(full_data)
    if history_df.empty:
        st.info("Ainda nao ha dados suficientes para o historico mensal.")
    else:
        st.line_chart(history_df, height=220)


def build_category_chart_data(month_data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    bank_df = combine_bank_expenses(month_data)
    if bank_df.empty:
        return pd.DataFrame()

    bank_df["categoria"] = bank_df["categoria"].replace("", "Sem categoria")
    return (
        bank_df.groupby("categoria")["valor"]
        .sum()
        .sort_values(ascending=False)
        .to_frame()
    )


def build_bank_chart_data(month_data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    bank_df = combine_bank_expenses(month_data)
    if bank_df.empty:
        return pd.DataFrame()

    bank_df["banco"] = bank_df["banco"].replace("", "Sem banco")
    return (
        bank_df.groupby("banco")["valor"]
        .sum()
        .sort_values(ascending=False)
        .to_frame()
    )


def build_house_bills_chart_data(house_bills_df: pd.DataFrame) -> pd.DataFrame:
    if house_bills_df.empty:
        return pd.DataFrame()

    return (
        house_bills_df.groupby("descricao")["valor"]
        .sum()
        .sort_values(ascending=False)
        .to_frame()
    )


def combine_bank_expenses(month_data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    frames = []
    for key in ["nubank", "manual_banks"]:
        df = month_data[key]
        if not df.empty:
            frames.append(df.copy())

    if not frames:
        return pd.DataFrame()

    combined_df = pd.concat(frames, ignore_index=True)
    for column in ["categoria", "banco"]:
        if column not in combined_df.columns:
            combined_df[column] = ""
        combined_df[column] = combined_df[column].fillna("").astype(str)
    combined_df["valor"] = pd.to_numeric(combined_df["valor"], errors="coerce").fillna(0.0)
    return combined_df


def render_bar_chart_or_empty(df: pd.DataFrame, column: str, empty_message: str) -> None:
    if df.empty:
        st.info(empty_message)
        return

    st.bar_chart(df[[column]], height=210)


def build_monthly_history(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    numanomes_values = collect_numanomes_options(data)
    rows = []

    for numanomes in sorted(numanomes_values):
        month_data = filter_month_data(data, numanomes)
        totals = calculate_month_totals(month_data)
        rows.append(
            {
                "NUMANOMES": numanomes,
                "Entradas": totals["income"],
                "Contas Casa": totals["house_bills"],
                "Cartoes/Bancos": totals["bank_accounts"],
                "Dizimo": totals["tithe"],
                "Saldo": totals["balance"],
            }
        )

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows).set_index("NUMANOMES")


def render_house_bills_table(
    house_bills_df: pd.DataFrame,
    selected_numanomes: str,
) -> None:
    st.markdown(
        f"""
        <div class="section-card">
            <h2>Tabela de contas da casa</h2>
            <p>Contas cadastradas para o NUMANOMES {selected_numanomes}.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if house_bills_df.empty:
        st.info("Nenhuma conta da casa cadastrada para este mes.")
        return

    table_df = house_bills_df[["NUMANOMES", "descricao", "valor", "status"]].copy()
    table_df = table_df.sort_values(["status", "descricao"])
    st.dataframe(
        table_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "NUMANOMES": st.column_config.TextColumn("NUMANOMES"),
            "descricao": st.column_config.TextColumn("Descricao", width="large"),
            "valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
            "status": st.column_config.TextColumn("Status"),
        },
    )


def render_placeholder(title: str, description: str) -> None:
    st.markdown(
        f"""
        <div class="page-heading">
            <span>Modulo</span>
            <h1>{title}</h1>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.subheader("Em construcao")
        st.write("Esta area ja esta criada para receber os proximos componentes.")
