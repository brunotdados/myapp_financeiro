from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from services.storage import load_table, save_table


PROJECT_ROOT = Path(__file__).resolve().parents[3]
NUBANK_EXPORT_PATH = PROJECT_ROOT / "data" / "exports" / "ControleFinanceiro.csv"
CATEGORY_CATALOG_PATH = PROJECT_ROOT / "data" / "processed" / "categorias_nubank.csv"
HOUSE_BILLS_PATH = PROJECT_ROOT / "data" / "processed" / "contas_casa.csv"
INCOME_ENTRIES_PATH = PROJECT_ROOT / "data" / "processed" / "entradas.csv"
MANUAL_BANK_ACCOUNTS_PATH = (
    PROJECT_ROOT / "data" / "processed" / "contas_banco_manuais.csv"
)
TITHE_PATH = PROJECT_ROOT / "data" / "processed" / "dizimo_mensal.csv"

CATEGORY_COLUMNS = ["categoria", "subcategoria"]
NUBANK_COLUMNS = [
    "data_compra",
    "descricao",
    "valor",
    "origem",
    "NUMANOMES",
    "banco",
    "categoria",
    "subcategoria",
]
HOUSE_BILLS_COLUMNS = ["id", "NUMANOMES", "descricao", "valor", "status"]
HOUSE_BILL_STATUS = ["Pendente", "Pago"]
INCOME_COLUMNS = ["id", "NUMANOMES", "descricao", "valor", "status"]
INCOME_STATUS = ["Previsto", "Recebido"]
MANUAL_BANK_COLUMNS = [
    "id",
    "data_compra",
    "descricao",
    "valor",
    "origem",
    "NUMANOMES",
    "banco",
    "categoria",
    "subcategoria",
]
TITHE_COLUMNS = [
    "id",
    "NUMANOMES",
    "salario_bruno",
    "dizimo_bruno",
    "salario_mayara",
    "dizimo_mayara",
    "total_dizimo",
    "status",
]
TITHE_STATUS = ["Pendente", "Pago"]
DEFAULT_BRUNO_SALARY = 6700.0
DEFAULT_MAYARA_SALARY = 5600.0
DEFAULT_CATALOG = pd.DataFrame(
    [
        {"categoria": "Alimentacao", "subcategoria": "Mercado"},
        {"categoria": "Moradia", "subcategoria": "Contas da casa"},
        {"categoria": "Transporte", "subcategoria": "Combustivel"},
        {"categoria": "Assinaturas", "subcategoria": "Servicos digitais"},
        {"categoria": "Lazer", "subcategoria": "Geral"},
        {"categoria": "Outros", "subcategoria": "Geral"},
    ]
)


def get_next_numanomes(reference_date: date | None = None) -> str:
    current = reference_date or date.today()
    year = current.year
    month = current.month + 1

    if month == 13:
        year += 1
        month = 1

    return f"{year}{month:02d}"


def format_currency(value: float) -> str:
    formatted = f"R$ {value:,.2f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def load_nubank_data() -> pd.DataFrame:
    df = load_table(
        table_name="nubank_lancamentos",
        columns=NUBANK_COLUMNS,
        csv_path=NUBANK_EXPORT_PATH,
    )
    if df.empty:
        return df

    df["NUMANOMES"] = df["NUMANOMES"].astype(str)

    needs_save = False
    for column in CATEGORY_COLUMNS:
        if column not in df.columns:
            df[column] = ""
            needs_save = True
        df[column] = df[column].fillna("").astype(str)

    if needs_save:
        save_nubank_data(df)

    return df


def save_nubank_data(df: pd.DataFrame) -> None:
    save_table(
        table_name="nubank_lancamentos",
        df=df,
        columns=NUBANK_COLUMNS,
        csv_path=NUBANK_EXPORT_PATH,
        delete_column="origem",
    )


def load_category_catalog() -> pd.DataFrame:
    catalog = load_table(
        table_name="categorias_nubank",
        columns=CATEGORY_COLUMNS,
        csv_path=CATEGORY_CATALOG_PATH,
    )
    if catalog.empty:
        catalog = DEFAULT_CATALOG.copy()
        save_category_catalog(catalog)

    for column in CATEGORY_COLUMNS:
        if column not in catalog.columns:
            catalog[column] = ""
        catalog[column] = catalog[column].fillna("").astype(str)

    return (
        catalog[CATEGORY_COLUMNS]
        .drop_duplicates()
        .sort_values(CATEGORY_COLUMNS)
        .reset_index(drop=True)
    )


def save_category_catalog(catalog: pd.DataFrame) -> None:
    save_table(
        table_name="categorias_nubank",
        df=catalog[CATEGORY_COLUMNS].drop_duplicates(),
        columns=CATEGORY_COLUMNS,
        csv_path=CATEGORY_CATALOG_PATH,
        delete_column="categoria",
    )


def add_category_pair(category: str, subcategory: str) -> None:
    category = category.strip()
    subcategory = subcategory.strip()

    if not category or not subcategory:
        raise ValueError("Informe categoria e subcategoria.")

    catalog = load_category_catalog()
    new_row = pd.DataFrame(
        [{"categoria": category, "subcategoria": subcategory}]
    )
    save_category_catalog(pd.concat([catalog, new_row], ignore_index=True))


def update_categorized_rows(
    full_df: pd.DataFrame,
    edited_month_df: pd.DataFrame,
) -> pd.DataFrame:
    updated_df = full_df.copy()

    for _, row in edited_month_df.iterrows():
        row_id = int(row["_row_id"])
        updated_df.loc[row_id, "categoria"] = row["categoria"]
        updated_df.loc[row_id, "subcategoria"] = row["subcategoria"]

    return updated_df


def load_house_bills() -> pd.DataFrame:
    df = load_table(
        table_name="contas_casa",
        columns=HOUSE_BILLS_COLUMNS,
        csv_path=HOUSE_BILLS_PATH,
    )
    if df.empty:
        return pd.DataFrame(columns=HOUSE_BILLS_COLUMNS)

    for column in HOUSE_BILLS_COLUMNS:
        if column not in df.columns:
            df[column] = "" if column != "valor" else 0.0

    df = df[HOUSE_BILLS_COLUMNS].copy()
    if df.empty:
        return df

    df["id"] = pd.to_numeric(df["id"], errors="coerce").fillna(0).astype(int)
    df["NUMANOMES"] = df["NUMANOMES"].astype(str)
    df["descricao"] = df["descricao"].fillna("").astype(str)
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0.0)
    df["status"] = df["status"].fillna("Pendente").astype(str)
    df.loc[~df["status"].isin(HOUSE_BILL_STATUS), "status"] = "Pendente"
    return df


def save_house_bills(df: pd.DataFrame) -> None:
    save_table(
        table_name="contas_casa",
        df=df,
        columns=HOUSE_BILLS_COLUMNS,
        csv_path=HOUSE_BILLS_PATH,
    )


def add_house_bill(numanomes: str, description: str, value: float, status: str) -> None:
    numanomes = numanomes.strip()
    description = description.strip()

    if len(numanomes) != 6 or not numanomes.isdigit():
        raise ValueError("NUMANOMES deve estar no formato AAAAMM, exemplo: 202606.")
    if not description:
        raise ValueError("Informe a descricao da conta.")
    if value <= 0:
        raise ValueError("Informe um valor maior que zero.")
    if status not in HOUSE_BILL_STATUS:
        raise ValueError("Status invalido.")

    df = load_house_bills()
    next_id = 1 if df.empty else int(df["id"].max()) + 1
    new_row = pd.DataFrame(
        [
            {
                "id": next_id,
                "NUMANOMES": numanomes,
                "descricao": description,
                "valor": value,
                "status": status,
            }
        ]
    )
    save_house_bills(pd.concat([df, new_row], ignore_index=True))


def update_house_bills(edited_df: pd.DataFrame) -> None:
    df = edited_df.copy()
    df["id"] = pd.to_numeric(df["id"], errors="coerce").fillna(0).astype(int)
    df["NUMANOMES"] = df["NUMANOMES"].astype(str)
    df["descricao"] = df["descricao"].fillna("").astype(str)
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0.0)
    df["status"] = df["status"].fillna("Pendente").astype(str)
    df.loc[~df["status"].isin(HOUSE_BILL_STATUS), "status"] = "Pendente"
    save_house_bills(df)


def load_income_entries() -> pd.DataFrame:
    df = load_table(
        table_name="entradas",
        columns=INCOME_COLUMNS,
        csv_path=INCOME_ENTRIES_PATH,
    )
    if df.empty:
        return pd.DataFrame(columns=INCOME_COLUMNS)

    for column in INCOME_COLUMNS:
        if column not in df.columns:
            df[column] = "" if column != "valor" else 0.0

    df = df[INCOME_COLUMNS].copy()
    if df.empty:
        return df

    df["id"] = pd.to_numeric(df["id"], errors="coerce").fillna(0).astype(int)
    df["NUMANOMES"] = df["NUMANOMES"].astype(str)
    df["descricao"] = df["descricao"].fillna("").astype(str)
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0.0)
    df["status"] = df["status"].fillna("Previsto").astype(str)
    df.loc[~df["status"].isin(INCOME_STATUS), "status"] = "Previsto"
    return df


def save_income_entries(df: pd.DataFrame) -> None:
    save_table(
        table_name="entradas",
        df=df,
        columns=INCOME_COLUMNS,
        csv_path=INCOME_ENTRIES_PATH,
    )


def add_income_entry(
    numanomes: str,
    description: str,
    value: float,
    status: str,
) -> None:
    numanomes = numanomes.strip()
    description = description.strip()

    if len(numanomes) != 6 or not numanomes.isdigit():
        raise ValueError("NUMANOMES deve estar no formato AAAAMM, exemplo: 202606.")
    if not description:
        raise ValueError("Informe a descricao da entrada.")
    if value <= 0:
        raise ValueError("Informe um valor maior que zero.")
    if status not in INCOME_STATUS:
        raise ValueError("Status invalido.")

    df = load_income_entries()
    next_id = 1 if df.empty else int(df["id"].max()) + 1
    new_row = pd.DataFrame(
        [
            {
                "id": next_id,
                "NUMANOMES": numanomes,
                "descricao": description,
                "valor": value,
                "status": status,
            }
        ]
    )
    save_income_entries(pd.concat([df, new_row], ignore_index=True))


def update_income_entries(edited_df: pd.DataFrame) -> None:
    df = edited_df.copy()
    df["id"] = pd.to_numeric(df["id"], errors="coerce").fillna(0).astype(int)
    df["NUMANOMES"] = df["NUMANOMES"].astype(str)
    df["descricao"] = df["descricao"].fillna("").astype(str)
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0.0)
    df["status"] = df["status"].fillna("Previsto").astype(str)
    df.loc[~df["status"].isin(INCOME_STATUS), "status"] = "Previsto"
    save_income_entries(df)


def load_manual_bank_accounts() -> pd.DataFrame:
    df = load_table(
        table_name="contas_banco_manuais",
        columns=MANUAL_BANK_COLUMNS,
        csv_path=MANUAL_BANK_ACCOUNTS_PATH,
    )
    if df.empty:
        return pd.DataFrame(columns=MANUAL_BANK_COLUMNS)

    for column in MANUAL_BANK_COLUMNS:
        if column not in df.columns:
            df[column] = "" if column != "valor" else 0.0

    df = df[MANUAL_BANK_COLUMNS].copy()
    if df.empty:
        return df

    df["id"] = pd.to_numeric(df["id"], errors="coerce").fillna(0).astype(int)
    df["data_compra"] = df["data_compra"].fillna("").astype(str)
    df["descricao"] = df["descricao"].fillna("").astype(str)
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0.0)
    df["origem"] = df["origem"].fillna("manual").astype(str)
    df["NUMANOMES"] = df["NUMANOMES"].astype(str)
    df["banco"] = df["banco"].fillna("").astype(str)
    df["categoria"] = df["categoria"].fillna("").astype(str)
    df["subcategoria"] = df["subcategoria"].fillna("").astype(str)
    return df


def save_manual_bank_accounts(df: pd.DataFrame) -> None:
    save_table(
        table_name="contas_banco_manuais",
        df=df,
        columns=MANUAL_BANK_COLUMNS,
        csv_path=MANUAL_BANK_ACCOUNTS_PATH,
    )


def add_manual_bank_account(
    purchase_date: date,
    description: str,
    value: float,
    bank: str,
    numanomes: str,
    category: str,
    subcategory: str,
) -> None:
    description = description.strip()
    bank = bank.strip().lower()
    numanomes = numanomes.strip()
    category = category.strip()
    subcategory = subcategory.strip()

    if len(numanomes) != 6 or not numanomes.isdigit():
        raise ValueError("NUMANOMES deve estar no formato AAAAMM, exemplo: 202606.")
    if not bank:
        raise ValueError("Informe o banco ou cartao.")
    if not description:
        raise ValueError("Informe a descricao do lancamento.")
    if value <= 0:
        raise ValueError("Informe um valor maior que zero.")

    df = load_manual_bank_accounts()
    next_id = 1 if df.empty else int(df["id"].max()) + 1
    new_row = pd.DataFrame(
        [
            {
                "id": next_id,
                "data_compra": purchase_date.isoformat(),
                "descricao": description,
                "valor": value,
                "origem": "manual",
                "NUMANOMES": numanomes,
                "banco": bank,
                "categoria": category,
                "subcategoria": subcategory,
            }
        ]
    )
    save_manual_bank_accounts(pd.concat([df, new_row], ignore_index=True))


def update_manual_bank_accounts(edited_df: pd.DataFrame) -> None:
    df = edited_df.copy()
    df["id"] = pd.to_numeric(df["id"], errors="coerce").fillna(0).astype(int)
    df["data_compra"] = df["data_compra"].fillna("").astype(str)
    df["descricao"] = df["descricao"].fillna("").astype(str)
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0.0)
    df["origem"] = df["origem"].fillna("manual").astype(str)
    df["NUMANOMES"] = df["NUMANOMES"].astype(str)
    df["banco"] = df["banco"].fillna("").astype(str).str.lower()
    df["categoria"] = df["categoria"].fillna("").astype(str)
    df["subcategoria"] = df["subcategoria"].fillna("").astype(str)
    save_manual_bank_accounts(df)


def load_monthly_tithe(year: int | None = None) -> pd.DataFrame:
    selected_year = year or date.today().year

    df = load_table(
        table_name="dizimo_mensal",
        columns=TITHE_COLUMNS,
        csv_path=TITHE_PATH,
    )
    if df.empty:
        df = build_default_tithe_table(selected_year)
        save_monthly_tithe(df)

    for column in TITHE_COLUMNS:
        if column not in df.columns:
            df[column] = "" if column not in _tithe_numeric_columns() else 0.0

    df = df[TITHE_COLUMNS].copy()
    if df.empty or not df["NUMANOMES"].astype(str).str.startswith(str(selected_year)).any():
        df = build_default_tithe_table(selected_year)
        save_monthly_tithe(df)

    return normalize_tithe_table(df)


def build_default_tithe_table(year: int) -> pd.DataFrame:
    rows = []
    for month in range(1, 13):
        salario_bruno = DEFAULT_BRUNO_SALARY
        salario_mayara = DEFAULT_MAYARA_SALARY
        dizimo_bruno = salario_bruno * 0.10
        dizimo_mayara = salario_mayara * 0.10
        rows.append(
            {
                "id": month,
                "NUMANOMES": f"{year}{month:02d}",
                "salario_bruno": salario_bruno,
                "dizimo_bruno": dizimo_bruno,
                "salario_mayara": salario_mayara,
                "dizimo_mayara": dizimo_mayara,
                "total_dizimo": dizimo_bruno + dizimo_mayara,
                "status": "Pendente",
            }
        )
    return pd.DataFrame(rows, columns=TITHE_COLUMNS)


def save_monthly_tithe(df: pd.DataFrame) -> None:
    normalized_df = normalize_tithe_table(df)
    save_table(
        table_name="dizimo_mensal",
        df=normalized_df,
        columns=TITHE_COLUMNS,
        csv_path=TITHE_PATH,
    )


def normalize_tithe_table(df: pd.DataFrame) -> pd.DataFrame:
    normalized_df = df.copy()
    normalized_df["id"] = pd.to_numeric(
        normalized_df["id"],
        errors="coerce",
    ).fillna(0).astype(int)
    normalized_df["NUMANOMES"] = normalized_df["NUMANOMES"].astype(str)

    for column in _tithe_numeric_columns():
        normalized_df[column] = pd.to_numeric(
            normalized_df[column],
            errors="coerce",
        ).fillna(0.0)

    normalized_df["dizimo_bruno"] = normalized_df["salario_bruno"] * 0.10
    normalized_df["dizimo_mayara"] = normalized_df["salario_mayara"] * 0.10
    normalized_df["total_dizimo"] = (
        normalized_df["dizimo_bruno"] + normalized_df["dizimo_mayara"]
    )
    normalized_df["status"] = normalized_df["status"].fillna("Pendente").astype(str)
    normalized_df.loc[~normalized_df["status"].isin(TITHE_STATUS), "status"] = (
        "Pendente"
    )

    return normalized_df[TITHE_COLUMNS]


def _tithe_numeric_columns() -> list[str]:
    return [
        "salario_bruno",
        "dizimo_bruno",
        "salario_mayara",
        "dizimo_mayara",
        "total_dizimo",
    ]
