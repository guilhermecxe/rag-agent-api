from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from src.services.files_service import FilesService
from src.di import get_files_service


router = APIRouter()

@router.post("/upload_file")
async def upload_file(
    file: UploadFile = File(...),
    files_service: FilesService = Depends(get_files_service)
):
    """Recebe um arquivo PDF e o indexa no banco vetorial.

    Args:
        file (UploadFile): Arquivo enviado via multipart/form-data.
        files_service (FilesService): Injetado pelo FastAPI via DI.

    Returns:
        dict: ``{"status": "success"}`` em caso de sucesso.

    Raises:
        HTTPException: 500 se ocorrer qualquer erro durante o upload ou indexação.
    """
    try:
        files_service.upload(
            file_bytes=await file.read(),
            file_title=file.filename,
            file_type="pdf"
        )

        return {
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_files")
async def get_files(files_service: FilesService = Depends(get_files_service)):
    """Retorna os nomes de todos os arquivos indexados.

    Args:
        files_service (FilesService): Injetado pelo FastAPI via DI.

    Returns:
        dict: ``{"files_names": list[str]}`` com os títulos únicos dos arquivos.

    Raises:
        HTTPException: 500 se ocorrer qualquer erro ao consultar o banco vetorial.
    """
    try:
        files_names = files_service.get_files()

        return {
            "files_names": files_names
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete_file")
async def delete_file(
    file_title: str,
    files_service: FilesService = Depends(get_files_service)
):
    """Remove um arquivo e todos os seus documentos do banco vetorial.

    Args:
        file_title (str): Título do arquivo a excluir (query parameter).
        files_service (FilesService): Injetado pelo FastAPI via DI.

    Returns:
        dict: ``{"status": "success"}`` em caso de sucesso.

    Raises:
        HTTPException: 500 se ocorrer qualquer erro durante a exclusão.
    """
    try:
        files_service.delete_file(file_title=file_title)
        return {
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search_documents")
async def search_documents(
    query: str,
    limit: int = 5,
    files_service: FilesService = Depends(get_files_service)
):
    """Busca documentos no banco vetorial por similaridade semântica.

    Args:
        query (str): Texto da consulta (query parameter).
        limit (int): Número máximo de resultados. Padrão: ``5``.
        files_service (FilesService): Injetado pelo FastAPI via DI.

    Returns:
        dict: ``{"documents": list[Document]}`` com os documentos encontrados.

    Raises:
        HTTPException: 500 se ocorrer qualquer erro durante a busca.
    """
    try:
        documents = files_service.search_documents(query=query, limit=limit)

        return {
            "documents": documents
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
