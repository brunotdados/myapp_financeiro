from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


def load_table(
    table_name: str,
    columns: list[str],
    csv_path: Path,
) -> pd.DataFrame:
    if is_supabase_configured():
        return load_supabase_table(table_name=table_name, columns=columns)

    if not csv_path.exists():
        return pd.DataFrame(columns=columns)

    return pd.read_csv(csv_path)


def save_table(
    table_name: str,
    df: pd.DataFrame,
    columns: list[str],
    csv_path: Path,
    delete_column: str = "id",
) -> None:
    normalized_df = df[columns].copy()

    if is_supabase_configured():
        replace_supabase_table(
            table_name=table_name,
            df=normalized_df,
            delete_column=delete_column,
        )
        return

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    normalized_df.to_csv(csv_path, index=False)


def is_supabase_configured() -> bool:
    return bool(get_secret("SUPABASE_URL") and get_secret("SUPABASE_KEY"))


def load_supabase_table(table_name: str, columns: list[str]) -> pd.DataFrame:
    client = get_supabase_client()
    try:
        response = client.table(table_name).select("*").execute()
    except Exception as exc:
        raise_supabase_error("carregar", table_name, exc)

    rows = response.data or []
    if not rows:
        return pd.DataFrame(columns=columns)

    df = pd.DataFrame(rows)
    for column in columns:
        if column not in df.columns:
            df[column] = None
    return df[columns]


def replace_supabase_table(
    table_name: str,
    df: pd.DataFrame,
    delete_column: str,
) -> None:
    client = get_supabase_client()

    try:
        if delete_column == "id":
            client.table(table_name).delete().neq("id", -1).execute()
        else:
            client.table(table_name).delete().neq(delete_column, "__never__").execute()

        if df.empty:
            return

        records = dataframe_to_records(df)
        client.table(table_name).insert(records).execute()
    except Exception as exc:
        raise_supabase_error("salvar", table_name, exc)


@st.cache_resource
def get_supabase_client() -> Any:
    try:
        from supabase import create_client
    except ImportError as exc:
        raise RuntimeError(
            "Supabase esta configurado, mas o pacote supabase nao foi instalado."
        ) from exc

    url = get_secret("SUPABASE_URL")
    key = get_secret("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("Configure SUPABASE_URL e SUPABASE_KEY.")

    return create_client(url, key)


def get_secret(name: str) -> str | None:
    value = os.getenv(name)
    if value:
        return value.strip()

    try:
        secret_value = st.secrets.get(name)
    except Exception:
        return None

    return str(secret_value).strip() if secret_value else None


def raise_supabase_error(action: str, table_name: str, exc: Exception) -> None:
    raise RuntimeError(
        f"Nao foi possivel {action} a tabela '{table_name}' no Supabase. "
        "Confira SUPABASE_URL, SUPABASE_KEY, se as tabelas foram criadas e se "
        f"o projeto Supabase esta ativo. Tipo do erro: {exc.__class__.__name__}."
    ) from exc


def dataframe_to_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    clean_df = df.where(pd.notna(df), None)
    records = clean_df.to_dict(orient="records")
    return [normalize_record(record) for record in records]


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    normalized = {}
    for key, value in record.items():
        if hasattr(value, "item"):
            value = value.item()
        normalized[key] = value
    return normalized
