import uuid
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.core.auth_utils import get_current_user
from app.models.user import User
from app.services.document_service import document_service

router = APIRouter(
    prefix="/api/v1/wallet",
    tags=["Wallet"],
)

class FolderCreateRequest(BaseModel):
    name: str

class FolderResponse(BaseModel):
    id: uuid.UUID
    name: str
    created_at: Any
    
    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):
    id: uuid.UUID
    filename: str
    file_type: str | None
    file_size: int | None
    created_at: Any
    
    class Config:
        from_attributes = True

@router.get("/folders", response_model=List[FolderResponse])
def get_folders(current_user: User = Depends(get_current_user)):
    return document_service.get_user_folders(current_user.id)

@router.post("/folders", response_model=FolderResponse)
def create_folder(request: FolderCreateRequest, current_user: User = Depends(get_current_user)):
    name = request.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Folder name is required")
    return document_service.create_folder(current_user.id, name)

@router.delete("/folders/{folder_id}")
def delete_folder(folder_id: uuid.UUID, current_user: User = Depends(get_current_user)):
    success = document_service.delete_folder(folder_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Folder not found")
    return {"status": "success"}

@router.get("/folders/{folder_id}/documents", response_model=List[DocumentResponse])
def get_documents(folder_id: uuid.UUID, current_user: User = Depends(get_current_user)):
    return document_service.get_documents_in_folder(folder_id, current_user.id)

@router.post("/folders/{folder_id}/documents", response_model=DocumentResponse)
async def upload_document(
    folder_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    document = await document_service.upload_document(folder_id, current_user.id, file)
    if not document:
        raise HTTPException(status_code=404, detail="Folder not found")
    return document

@router.delete("/documents/{document_id}")
def delete_document(document_id: uuid.UUID, current_user: User = Depends(get_current_user)):
    success = document_service.delete_document(document_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "success"}

@router.get("/documents/{document_id}/download")
def download_document(document_id: uuid.UUID, current_user: User = Depends(get_current_user)):
    document = document_service.get_document(document_id, current_user.id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return FileResponse(
        path=document.file_path,
        filename=document.filename,
        media_type=document.file_type or "application/octet-stream"
    )
