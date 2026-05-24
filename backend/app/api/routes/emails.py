import imaplib

from fastapi import APIRouter, HTTPException, Query

from app.core.config import settings
from app.schemas.email import EmailSearchResponse
from app.schemas.nubank import NubankStatementPipelineResponse
from app.services.nubank_email_service import NubankEmailService
from app.services.nubank_statement_pipeline import NubankStatementPipeline

router = APIRouter(prefix="/emails", tags=["emails"])


@router.get("/nubank", response_model=EmailSearchResponse)
def buscar_emails_nubank(
    limit: int = Query(default=settings.nubank_email_limit, ge=1, le=100),
) -> EmailSearchResponse:
    service = NubankEmailService(settings=settings)

    try:
        return service.search(limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except imaplib.IMAP4.error as exc:
        raise HTTPException(
            status_code=502,
            detail="Falha ao conectar ou autenticar no Gmail. Confira email e senha de app.",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/nubank/extrato-fatura/mais-recente", response_model=EmailSearchResponse)
def buscar_extrato_fatura_nubank_mais_recente() -> EmailSearchResponse:
    service = NubankEmailService(settings=settings)

    try:
        return service.search_latest_statement()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except imaplib.IMAP4.error as exc:
        raise HTTPException(
            status_code=502,
            detail="Falha ao conectar ou autenticar no Gmail. Confira email e senha de app.",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post(
    "/nubank/extrato-fatura/mais-recente/processar",
    response_model=NubankStatementPipelineResponse,
)
def processar_extrato_fatura_nubank_mais_recente() -> NubankStatementPipelineResponse:
    pipeline = NubankStatementPipeline(settings=settings)

    try:
        result = pipeline.run_latest_statement()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except imaplib.IMAP4.error as exc:
        raise HTTPException(
            status_code=502,
            detail="Falha ao conectar ou autenticar no Gmail. Confira email e senha de app.",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return NubankStatementPipelineResponse(
        saved_attachments=[
            {
                "account_name": attachment.account_name,
                "filename": attachment.filename,
                "path": str(attachment.path),
            }
            for attachment in result.saved_attachments
        ],
        output_path=str(result.output_path),
        rows=result.rows,
        columns=result.columns,
    )
