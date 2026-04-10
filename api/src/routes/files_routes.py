from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from src.services.files_service import FilesService
from src.di import get_files_service


router = APIRouter()

@router.post("/upload_file")
async def upload_file(
    file: UploadFile = File(...),
    files_service: FilesService = Depends(get_files_service)
):
    """
    Endpoint to upload a file. The file is read and its content is returned as a string.
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
    try:
        documents = files_service.search_documents(query=query, limit=limit)
        
        return {
            "documents": documents
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
