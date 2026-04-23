from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File

from src.services.sources_service import SourcesService
from src.di import get_sources_service


router = APIRouter()

@router.post("/upload_source")
async def upload_source(
    file: UploadFile = File(...),
    sources_service: SourcesService = Depends(get_sources_service)
):
    """Recebe um arquivo PDF e o indexa no banco vetorial como source.

    Args:
        file (UploadFile): Arquivo enviado via multipart/form-data.
        sources_service (SourcesService): Injetado pelo FastAPI via DI.

    Returns:
        dict: ``{"status": "success"}`` em caso de sucesso.

    Raises:
        HTTPException: 500 se ocorrer qualquer erro durante o upload ou indexação.
    """
    try:
        sources_service.upload(
            source_bytes=await file.read(),
            source_title=file.filename,
            source_type="pdf"
        )

        return {
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_sources")
async def get_sources(sources_service: SourcesService = Depends(get_sources_service)):
    """Retorna os nomes de todos os sources indexados.

    Args:
        sources_service (SourcesService): Injetado pelo FastAPI via DI.

    Returns:
        dict: ``{"source_names": list[str]}`` com os títulos únicos dos sources.

    Raises:
        HTTPException: 500 se ocorrer qualquer erro ao consultar o banco vetorial.
    """
    try:
        source_names = sources_service.get_sources()

        return {
            "source_names": source_names
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search_sources_regex")
async def search_sources_regex(
    pattern: str,
    page: int = 1,
    sources_service: SourcesService = Depends(get_sources_service)
):
    try:
        if len(pattern) < 2:
            raise ValueError("Por favor, forneça uma string maior do que 1 caractere.")

        result = sources_service.search_sources_regex(pattern=pattern, page=page)

        return {
            "sources": result["relevant_sources"],
            "current_page": result["current_page"],
            "last_page": result["last_page"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete_source")
async def delete_source(
    source_title: str,
    sources_service: SourcesService = Depends(get_sources_service)
):
    """Remove um source e todos os seus documents do banco vetorial.

    Args:
        source_title (str): Título do source a excluir (query parameter).
        sources_service (SourcesService): Injetado pelo FastAPI via DI.

    Returns:
        dict: ``{"status": "success"}`` em caso de sucesso.

    Raises:
        HTTPException: 500 se ocorrer qualquer erro durante a exclusão.
    """
    try:
        sources_service.delete_source(source_title=source_title)
        return {
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_excerpt")
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
        dict: ``{"excerpt": Document}`` com o trecho encontrado.

    Raises:
        HTTPException: 500 se ocorrer qualquer erro, incluindo trecho não encontrado.
    """
    try:
        excerpt = sources_service.get_excerpt(source_name=source_name, index=index)
        return {"excerpt": excerpt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search_excerpts_regex")
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
        dict: Dicionário com as chaves:
            - ``excerpts`` (list): Trechos encontrados na página atual.
            - ``current_page`` (int): Página atual.
            - ``last_page`` (int): Última página disponível.

    Raises:
        HTTPException: 500 se ocorrer qualquer erro durante a busca.
    """
    try:
        result = sources_service.search_excerpts_regex(
            pattern=pattern, sources=sources, page=page
        )

        return {
            "excerpts": result["relevant_excerpts"],
            "current_page": result["current_page"],
            "last_page": result["last_page"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search_excerpts_semantic")
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
        dict: ``{"excerpts": list[Document]}`` com os trechos mais relevantes.

    Raises:
        HTTPException: 500 se ocorrer qualquer erro durante a busca.
    """
    try:
        excerpts = sources_service.search_excerpts_semantic(
            query=query, source_names=source_names
        )

        return {"excerpts": excerpts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search_documents")
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
        dict: ``{"documents": list[Document]}`` com os documents encontrados.

    Raises:
        HTTPException: 500 se ocorrer qualquer erro durante a busca.
    """
    try:
        documents = sources_service.search_documents(query=query, limit=limit)

        return {
            "documents": documents
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
