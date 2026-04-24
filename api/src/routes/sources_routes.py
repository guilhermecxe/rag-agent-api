from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File

from src.services.sources_service import SourcesService
from src.di import get_sources_service
from src.schemas.sources import (
    DocumentModel,
    SourcesPage,
    StatusResponse,
    GetSourcesResponse,
    SearchSourcesRegexResponse,
    GetExcerptResponse,
    SearchExcerptsRegexResponse,
    SearchExcerptsSemanticResponse,
    SearchDocumentsResponse,
)


router = APIRouter()

@router.post("/upload_source", response_model=StatusResponse)
async def upload_source(
    file: UploadFile = File(...),
    sources_service: SourcesService = Depends(get_sources_service)
):
    """Recebe um arquivo PDF e o indexa no banco vetorial como source.

    Args:
        file (UploadFile): Arquivo enviado via multipart/form-data.
        sources_service (SourcesService): Injetado pelo FastAPI via DI.

    Returns:
        StatusResponse: ``{"status": "success"}`` em caso de sucesso.

    Raises:
        HTTPException: 500 se ocorrer qualquer erro durante o upload ou indexação.
    """
    try:
        await sources_service.upload(
            source_bytes=await file.read(),
            source_title=file.filename,
            source_type="pdf"
        )

        return StatusResponse(status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_sources", response_model=GetSourcesResponse)
async def get_sources(
    page: int = 1,
    sources_service: SourcesService = Depends(get_sources_service)
):
    """Retorna os nomes de todos os sources indexados.

    Args:
        page (int): Página de resultados. Padrão: ``1``.
        sources_service (SourcesService): Injetado pelo FastAPI via DI.

    Returns:
        GetSourcesResponse: Página de títulos de sources.

    Raises:
        HTTPException: 500 se ocorrer qualquer erro ao consultar o banco vetorial.
    """
    try:
        result = sources_service.get_sources(page=page)

        return GetSourcesResponse(sources=SourcesPage(**result))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search_sources_regex", response_model=SearchSourcesRegexResponse)
async def search_sources_regex(
    pattern: str,
    page: int = 1,
    sources_service: SourcesService = Depends(get_sources_service)
):
    try:
        if len(pattern) < 2:
            raise ValueError("Por favor, forneça uma string maior do que 1 caractere.")

        result = sources_service.search_sources_regex(pattern=pattern, page=page)

        return SearchSourcesRegexResponse(
            sources=result["relevant_sources"],
            current_page=result["current_page"],
            last_page=result["last_page"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete_source", response_model=StatusResponse)
async def delete_source(
    source_title: str,
    sources_service: SourcesService = Depends(get_sources_service)
):
    """Remove um source e todos os seus documents do banco vetorial.

    Args:
        source_title (str): Título do source a excluir (query parameter).
        sources_service (SourcesService): Injetado pelo FastAPI via DI.

    Returns:
        StatusResponse: ``{"status": "success"}`` em caso de sucesso.

    Raises:
        HTTPException: 500 se ocorrer qualquer erro durante a exclusão.
    """
    try:
        sources_service.delete_source(source_title=source_title)
        return StatusResponse(status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_excerpt", response_model=GetExcerptResponse)
async def get_excerpt(
    source_name: str,
    index: int,
    sources_service: SourcesService = Depends(get_sources_service)
):
    """Retorna um trecho específico de um source pelo seu índice incremental.

    Args:
        source_name (str): Título do source de origem.
        index (int): Índice incremental da página (base 1).
        sources_service (SourcesService): Injetado pelo FastAPI via DI.

    Returns:
        GetExcerptResponse: Trecho encontrado.

    Raises:
        HTTPException: 500 se ocorrer qualquer erro, incluindo trecho não encontrado.
    """
    try:
        excerpt = sources_service.get_excerpt(source_name=source_name, index=index)
        return GetExcerptResponse(
            excerpt=DocumentModel(
                page_content=excerpt.page_content,
                metadata=excerpt.metadata
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search_excerpts_regex", response_model=SearchExcerptsRegexResponse)
async def search_excerpts_regex(
    pattern: str,
    sources: list[str] | None = Query(default=None),
    page: int = 1,
    sources_service: SourcesService = Depends(get_sources_service)
):
    """Busca trechos de documents cujo conteúdo corresponde a um padrão regex.

    Args:
        pattern (str): Expressão regular aplicada ao conteúdo dos documents.
        sources (list[str] | None): Títulos dos sources que limitam a busca
            (query parameter repetível). Se omitido, busca em todos os sources.
        page (int): Página de resultados. Padrão: ``1``.
        sources_service (SourcesService): Injetado pelo FastAPI via DI.

    Returns:
        SearchExcerptsRegexResponse: Trechos encontrados na página atual.

    Raises:
        HTTPException: 500 se ocorrer qualquer erro durante a busca.
    """
    try:
        result = sources_service.search_excerpts_regex(
            pattern=pattern, sources=sources, page=page
        )

        return SearchExcerptsRegexResponse(
            excerpts=[
                DocumentModel(page_content=e.page_content, metadata=e.metadata)
                for e in result["relevant_excerpts"]
            ],
            current_page=result["current_page"],
            last_page=result["last_page"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search_excerpts_semantic", response_model=SearchExcerptsSemanticResponse)
async def search_excerpts_semantic(
    query: str,
    source_names: list[str] | None = Query(default=None),
    sources_service: SourcesService = Depends(get_sources_service)
):
    """Busca trechos de documents semanticamente similares à query.

    Args:
        query (str): Texto da consulta.
        source_names (list[str] | None): Títulos dos sources que limitam a busca
            (query parameter repetível). Se omitido, busca em todos os sources.
        sources_service (SourcesService): Injetado pelo FastAPI via DI.

    Returns:
        SearchExcerptsSemanticResponse: Trechos mais relevantes.

    Raises:
        HTTPException: 500 se ocorrer qualquer erro durante a busca.
    """
    try:
        excerpts = sources_service.search_excerpts_semantic(
            query=query, source_names=source_names
        )

        return SearchExcerptsSemanticResponse(
            excerpts=[
                DocumentModel(page_content=e.page_content, metadata=e.metadata)
                for e in excerpts
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search_documents", response_model=SearchDocumentsResponse)
async def search_documents(
    query: str,
    limit: int = 5,
    sources_service: SourcesService = Depends(get_sources_service)
):
    """Busca documents no banco vetorial por similaridade semântica.

    Args:
        query (str): Texto da consulta (query parameter).
        limit (int): Número máximo de resultados. Padrão: ``5``.
        sources_service (SourcesService): Injetado pelo FastAPI via DI.

    Returns:
        SearchDocumentsResponse: Documents encontrados.

    Raises:
        HTTPException: 500 se ocorrer qualquer erro durante a busca.
    """
    try:
        documents = sources_service.search_documents(query=query, limit=limit)

        return SearchDocumentsResponse(
            documents=[
                DocumentModel(page_content=d.page_content, metadata=d.metadata)
                for d in documents
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
