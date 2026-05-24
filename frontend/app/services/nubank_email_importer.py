from __future__ import annotations

from dataclasses import dataclass
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from io import BytesIO
import imaplib
from pathlib import Path

import pandas as pd

from services.finance_data import NUBANK_COLUMNS, load_nubank_data, save_nubank_data
from services.storage import get_secret


@dataclass(frozen=True)
class EmailAccount:
    name: str
    email: str
    app_password: str


@dataclass(frozen=True)
class EmailAttachment:
    account_name: str
    filename: str
    content: bytes


@dataclass(frozen=True)
class NubankImportResult:
    rows: int
    accounts: list[str]
    attachments: list[str]


BANK_NAMES = {
    "bruno": "nubank bruno",
    "mayara": "nubank mayara",
}
CSV_COLUMN_NAMES = {
    "date": "data_compra",
    "title": "descricao",
    "amount": "valor",
}
CATEGORY_COLUMNS = ["categoria", "subcategoria"]
CATEGORY_MERGE_KEYS = [
    "data_compra",
    "descricao",
    "valor",
    "origem",
    "NUMANOMES",
    "banco",
]


def import_latest_nubank_statements() -> NubankImportResult:
    accounts = get_configured_accounts()
    attachments = download_latest_statement_attachments(accounts)

    if not attachments:
        raise ValueError("Nenhum anexo CSV do Nubank foi encontrado nos emails recentes.")

    imported_df = consolidate_attachments(attachments)
    final_df = preserve_existing_categories(imported_df, load_nubank_data())
    save_nubank_data(final_df)

    return NubankImportResult(
        rows=len(final_df),
        accounts=sorted({attachment.account_name for attachment in attachments}),
        attachments=[attachment.filename for attachment in attachments],
    )


def get_configured_accounts() -> list[EmailAccount]:
    accounts: list[EmailAccount] = []
    account_settings = [
        ("bruno", "BRUNO_EMAIL", "BRUNO_EMAIL_APP_PASSWORD"),
        ("mayara", "MAYARA_EMAIL", "MAYARA_EMAIL_APP_PASSWORD"),
    ]

    for name, email_key, password_key in account_settings:
        email = get_secret(email_key)
        password = get_secret(password_key)
        if email and password:
            accounts.append(
                EmailAccount(name=name, email=email, app_password=password)
            )

    if not accounts:
        raise ValueError(
            "Configure BRUNO_EMAIL, BRUNO_EMAIL_APP_PASSWORD, MAYARA_EMAIL e "
            "MAYARA_EMAIL_APP_PASSWORD nos secrets do Streamlit."
        )

    return accounts


def download_latest_statement_attachments(
    accounts: list[EmailAccount],
) -> list[EmailAttachment]:
    host = get_secret("GMAIL_IMAP_HOST") or "imap.gmail.com"
    port = int(get_secret("GMAIL_IMAP_PORT") or "993")
    subject = get_secret("NUBANK_STATEMENT_SUBJECT") or "Extrato da fatura do Cartão Nubank"
    query = get_secret("NUBANK_GMAIL_QUERY") or "subject:Extrato subject:fatura newer_than:365d"

    attachments: list[EmailAttachment] = []
    for account in accounts:
        with imaplib.IMAP4_SSL(host, port) as mailbox:
            mailbox._encoding = "utf-8"
            mailbox.login(account.email, account.app_password)
            mailbox.select("INBOX")

            latest_message = find_latest_message_by_subject(
                mailbox=mailbox,
                query=query,
                subject=subject,
            )
            if latest_message is None:
                continue

            for part in latest_message.iter_attachments():
                filename = part.get_filename()
                if not filename:
                    continue

                safe_filename = Path(filename).name
                if Path(safe_filename).suffix.lower() != ".csv":
                    continue

                content = part.get_payload(decode=True)
                if not content:
                    continue

                attachments.append(
                    EmailAttachment(
                        account_name=account.name,
                        filename=safe_filename,
                        content=content,
                    )
                )

    return attachments


def find_latest_message_by_subject(
    mailbox: imaplib.IMAP4_SSL,
    query: str,
    subject: str,
) -> EmailMessage | None:
    encoded_query = encode_gmail_raw_query(query)
    status, data = mailbox.uid("search", None, "X-GM-RAW", encoded_query)
    if status != "OK":
        raise RuntimeError("Falha ao buscar emails no Gmail.")

    uids = data[0].split()
    for uid in reversed(uids):
        message = fetch_message(mailbox, uid)
        if str(message.get("Subject", "")) == subject:
            return message

    return None


def fetch_message(mailbox: imaplib.IMAP4_SSL, uid: bytes) -> EmailMessage:
    status, data = mailbox.uid("fetch", uid, "(RFC822)")
    if status != "OK":
        raise RuntimeError(f"Falha ao ler email UID {uid.decode()}.")

    for item in data:
        if isinstance(item, tuple) and isinstance(item[1], bytes):
            return BytesParser(policy=policy.default).parsebytes(item[1])

    raise RuntimeError("Resposta de email sem conteudo RFC822.")


def encode_gmail_raw_query(query: str) -> str:
    escaped_query = query.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped_query}"'


def consolidate_attachments(attachments: list[EmailAttachment]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    for attachment in attachments:
        df = pd.read_csv(BytesIO(attachment.content), sep=",")
        df["origem"] = attachment.filename
        df["NUMANOMES"] = extract_year_month(attachment.filename)
        df["banco"] = BANK_NAMES.get(attachment.account_name, attachment.account_name)
        frames.append(df)

    if not frames:
        raise ValueError("Nenhum CSV do Nubank foi encontrado para consolidar.")

    final_df = pd.concat(frames, ignore_index=True)
    required_columns = {"date", "title", "amount", "origem", "NUMANOMES", "banco"}
    missing_columns = required_columns.difference(final_df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"O CSV do Nubank esta sem as colunas esperadas: {missing}.")

    final_df["amount"] = pd.to_numeric(final_df["amount"], errors="coerce").fillna(0.0)
    final_df = final_df[final_df["amount"] >= 0].copy()
    final_df = final_df.rename(columns=CSV_COLUMN_NAMES)

    for column in CATEGORY_COLUMNS:
        final_df[column] = ""

    return normalize_nubank_df(final_df)


def extract_year_month(file_name: str) -> str:
    if file_name.startswith("Nubank_") and len(file_name) >= 14:
        return file_name[7:14].replace("-", "")
    return "Desconhecido"


def preserve_existing_categories(
    new_df: pd.DataFrame,
    existing_df: pd.DataFrame,
) -> pd.DataFrame:
    if existing_df.empty:
        return normalize_nubank_df(new_df)

    if not all(column in existing_df.columns for column in CATEGORY_COLUMNS):
        return normalize_nubank_df(new_df)

    if not all(column in existing_df.columns for column in CATEGORY_MERGE_KEYS):
        return normalize_nubank_df(new_df)

    new_with_key = add_occurrence_key(new_df)
    existing_with_key = add_occurrence_key(existing_df)

    lookup = existing_with_key[
        CATEGORY_MERGE_KEYS + ["_occurrence"] + CATEGORY_COLUMNS
    ]
    merged_df = new_with_key.drop(columns=CATEGORY_COLUMNS).merge(
        lookup,
        on=CATEGORY_MERGE_KEYS + ["_occurrence"],
        how="left",
    )
    merged_df = merged_df.drop(columns=["_occurrence"])

    for column in CATEGORY_COLUMNS:
        merged_df[column] = merged_df[column].fillna("").astype(str)

    return normalize_nubank_df(merged_df)


def add_occurrence_key(df: pd.DataFrame) -> pd.DataFrame:
    keyed_df = normalize_nubank_df(df)
    keyed_df["_occurrence"] = keyed_df.groupby(
        CATEGORY_MERGE_KEYS,
        dropna=False,
    ).cumcount()
    return keyed_df


def normalize_nubank_df(df: pd.DataFrame) -> pd.DataFrame:
    normalized_df = df.copy()

    for column in NUBANK_COLUMNS:
        if column not in normalized_df.columns:
            normalized_df[column] = "" if column != "valor" else 0.0

    normalized_df["data_compra"] = normalized_df["data_compra"].fillna("").astype(str)
    normalized_df["descricao"] = normalized_df["descricao"].fillna("").astype(str)
    normalized_df["valor"] = pd.to_numeric(
        normalized_df["valor"],
        errors="coerce",
    ).fillna(0.0)
    normalized_df["origem"] = normalized_df["origem"].fillna("").astype(str)
    normalized_df["NUMANOMES"] = normalized_df["NUMANOMES"].fillna("").astype(str)
    normalized_df["banco"] = normalized_df["banco"].fillna("").astype(str)
    normalized_df["categoria"] = normalized_df["categoria"].fillna("").astype(str)
    normalized_df["subcategoria"] = normalized_df["subcategoria"].fillna("").astype(str)

    return normalized_df[NUBANK_COLUMNS]
