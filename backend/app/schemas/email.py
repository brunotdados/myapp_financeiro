from pydantic import BaseModel, Field


class EmailSummary(BaseModel):
    account_name: str
    uid: str
    sender: str
    subject: str
    sent_at: str | None = None
    attachments: list[str] = Field(default_factory=list)
    body_preview: str | None = None


class EmailSearchResponse(BaseModel):
    query: str
    total: int
    emails: list[EmailSummary]
