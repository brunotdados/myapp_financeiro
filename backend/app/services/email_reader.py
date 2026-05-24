from dataclasses import dataclass
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
import imaplib
from pathlib import Path


@dataclass(frozen=True)
class EmailAccount:
    name: str
    email: str
    app_password: str


@dataclass(frozen=True)
class EmailMessageSummary:
    account_name: str
    uid: str
    sender: str
    subject: str
    sent_at: str | None
    attachments: list[str]
    body_preview: str | None


@dataclass(frozen=True)
class EmailAttachment:
    account_name: str
    uid: str
    filename: str
    content: bytes


class GmailImapReader:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

    def search_messages(
        self,
        account: EmailAccount,
        query: str,
        limit: int,
    ) -> list[EmailMessageSummary]:
        with imaplib.IMAP4_SSL(self.host, self.port) as mailbox:
            mailbox._encoding = "utf-8"
            mailbox.login(account.email, account.app_password)
            mailbox.select("INBOX")

            encoded_query = self._encode_gmail_raw_query(query)
            status, data = mailbox.uid("search", None, "X-GM-RAW", encoded_query)
            if status != "OK":
                raise RuntimeError(f"Falha ao buscar emails da conta {account.name}.")

            uids = data[0].split()
            selected_uids = list(reversed(uids))[:limit]

            return [
                self._fetch_summary(mailbox, account_name=account.name, uid=uid)
                for uid in selected_uids
            ]

    def download_attachments(
        self,
        account: EmailAccount,
        uid: str,
        allowed_suffixes: set[str] | None = None,
    ) -> list[EmailAttachment]:
        with imaplib.IMAP4_SSL(self.host, self.port) as mailbox:
            mailbox._encoding = "utf-8"
            mailbox.login(account.email, account.app_password)
            mailbox.select("INBOX")

            status, data = mailbox.uid("fetch", uid.encode(), "(RFC822)")
            if status != "OK":
                raise RuntimeError(f"Falha ao baixar anexos do email UID {uid}.")

            raw_message = self._extract_raw_message(data)
            message = BytesParser(policy=policy.default).parsebytes(raw_message)
            attachments: list[EmailAttachment] = []

            for part in message.iter_attachments():
                filename = part.get_filename()
                if not filename:
                    continue

                safe_filename = Path(filename).name
                suffix = Path(safe_filename).suffix.lower()
                if allowed_suffixes and suffix not in allowed_suffixes:
                    continue

                content = part.get_payload(decode=True)
                if not content:
                    continue

                attachments.append(
                    EmailAttachment(
                        account_name=account.name,
                        uid=uid,
                        filename=safe_filename,
                        content=content,
                    )
                )

            return attachments

    def _fetch_summary(
        self,
        mailbox: imaplib.IMAP4_SSL,
        account_name: str,
        uid: bytes,
    ) -> EmailMessageSummary:
        status, data = mailbox.uid("fetch", uid, "(RFC822)")
        if status != "OK":
            raise RuntimeError(f"Falha ao ler email UID {uid.decode()}.")

        raw_message = self._extract_raw_message(data)
        message = BytesParser(policy=policy.default).parsebytes(raw_message)

        return EmailMessageSummary(
            account_name=account_name,
            uid=uid.decode(),
            sender=str(message.get("From", "")),
            subject=str(message.get("Subject", "")),
            sent_at=str(message.get("Date", "")) or None,
            attachments=self._extract_attachment_names(message),
            body_preview=self._extract_body_preview(message),
        )

    @staticmethod
    def _extract_raw_message(fetch_data: list[bytes | tuple]) -> bytes:
        for item in fetch_data:
            if isinstance(item, tuple) and isinstance(item[1], bytes):
                return item[1]
        raise RuntimeError("Resposta de email sem conteudo RFC822.")

    @staticmethod
    def _encode_gmail_raw_query(query: str) -> str:
        escaped_query = query.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped_query}"'

    @staticmethod
    def _extract_attachment_names(message: EmailMessage) -> list[str]:
        return [
            part.get_filename()
            for part in message.iter_attachments()
            if part.get_filename()
        ]

    @staticmethod
    def _extract_body_preview(message: EmailMessage) -> str | None:
        body = message.get_body(preferencelist=("plain", "html"))
        if body is None:
            return None

        content = body.get_content()
        normalized = " ".join(content.split())
        if not normalized:
            return None

        return normalized[:300]
