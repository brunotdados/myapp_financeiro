from app.core.config import Settings
from app.schemas.email import EmailSearchResponse, EmailSummary
from app.services.email_reader import EmailAccount, GmailImapReader


class NubankEmailService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.reader = GmailImapReader(
            host=settings.gmail_imap_host,
            port=settings.gmail_imap_port,
        )

    def search(self, limit: int) -> EmailSearchResponse:
        accounts = self.get_configured_accounts()
        emails: list[EmailSummary] = []

        for account in accounts:
            messages = self.reader.search_messages(
                account=account,
                query=self.settings.nubank_gmail_query,
                limit=limit,
            )
            emails.extend(EmailSummary(**message.__dict__) for message in messages)

        return EmailSearchResponse(
            query=self.settings.nubank_gmail_query,
            total=len(emails),
            emails=emails,
        )

    def search_latest_statement(self) -> EmailSearchResponse:
        query = self._build_statement_query()
        accounts = self.get_configured_accounts()
        emails: list[EmailSummary] = []

        for account in accounts:
            messages = self.reader.search_messages(
                account=account,
                query=query,
                limit=50,
            )
            latest_statement = next(
                (
                    message
                    for message in messages
                    if message.subject == self.settings.nubank_statement_subject
                ),
                None,
            )

            if latest_statement:
                emails.append(EmailSummary(**latest_statement.__dict__))

        return EmailSearchResponse(
            query=query,
            total=len(emails),
            emails=emails,
        )

    def _build_statement_query(self) -> str:
        return "subject:Extrato subject:fatura newer_than:365d"

    def get_configured_accounts(self) -> list[EmailAccount]:
        accounts: list[EmailAccount] = []

        if self.settings.bruno_email and self.settings.bruno_email_app_password:
            accounts.append(
                EmailAccount(
                    name="bruno",
                    email=self.settings.bruno_email,
                    app_password=self.settings.bruno_email_app_password,
                )
            )

        if self.settings.mayara_email and self.settings.mayara_email_app_password:
            accounts.append(
                EmailAccount(
                    name="mayara",
                    email=self.settings.mayara_email,
                    app_password=self.settings.mayara_email_app_password,
                )
            )

        if not accounts:
            raise ValueError("Nenhuma conta Gmail foi configurada no .env.")

        return accounts
