from pydantic import BaseModel


class SavedAttachmentResponse(BaseModel):
    account_name: str
    filename: str
    path: str


class NubankStatementPipelineResponse(BaseModel):
    saved_attachments: list[SavedAttachmentResponse]
    output_path: str
    rows: int
    columns: list[str]
