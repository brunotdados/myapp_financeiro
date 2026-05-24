from dataclasses import dataclass
from pathlib import Path

from app.core.config import Settings
from app.services.email_reader import EmailAccount
from app.services.nubank_csv_service import NubankCsvService
from app.services.nubank_email_service import NubankEmailService


@dataclass(frozen=True)
class SavedAttachment:
    account_name: str
    filename: str
    path: Path


@dataclass(frozen=True)
class StatementPipelineResult:
    saved_attachments: list[SavedAttachment]
    output_path: Path
    rows: int
    columns: list[str]


class NubankStatementPipeline:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.email_service = NubankEmailService(settings=settings)
        self.csv_service = NubankCsvService()
        self.project_root = Path(__file__).resolve().parents[3]
        self.raw_root = self.project_root / "data" / "raw" / "nubank"
        self.output_path = self.project_root / "data" / "exports" / "ControleFinanceiro.csv"

    def run_latest_statement(self) -> StatementPipelineResult:
        accounts = {
            account.name: account
            for account in self.email_service.get_configured_accounts()
        }
        latest_emails = self.email_service.search_latest_statement().emails
        saved_attachments: list[SavedAttachment] = []
        files_by_account: dict[str, list[Path]] = {}

        for email in latest_emails:
            account = accounts[email.account_name]
            downloaded_files = self._download_csv_attachments(account=account, uid=email.uid)
            files_by_account[email.account_name] = downloaded_files
            saved_attachments.extend(
                SavedAttachment(
                    account_name=email.account_name,
                    filename=file_path.name,
                    path=file_path,
                )
                for file_path in downloaded_files
            )

        consolidation = self.csv_service.consolidate_files(
            files_by_account=files_by_account,
            output_path=self.output_path,
        )

        return StatementPipelineResult(
            saved_attachments=saved_attachments,
            output_path=consolidation.output_path,
            rows=consolidation.rows,
            columns=consolidation.columns,
        )

    def _download_csv_attachments(self, account: EmailAccount, uid: str) -> list[Path]:
        attachments = self.email_service.reader.download_attachments(
            account=account,
            uid=uid,
            allowed_suffixes={".csv"},
        )
        account_dir = self.raw_root / account.name
        account_dir.mkdir(parents=True, exist_ok=True)

        saved_files: list[Path] = []
        for attachment in attachments:
            file_path = account_dir / attachment.filename
            file_path.write_bytes(attachment.content)
            saved_files.append(file_path)

        return saved_files
