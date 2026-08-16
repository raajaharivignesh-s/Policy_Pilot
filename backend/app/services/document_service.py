import os
import uuid
import logging
from typing import Optional, List
from fastapi import UploadFile
import fitz  # PyMuPDF

from app.database.session import SessionLocal
from app.models.document import DocumentFolder, Document

logger = logging.getLogger(__name__)

STORAGE_DIR = "storage/documents"

class DocumentService:
    def __init__(self):
        os.makedirs(STORAGE_DIR, exist_ok=True)

    def extract_text_from_pdf(self, file_path: str) -> Optional[str]:
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            return None

    def extract_text_from_image(self, file_path: str) -> Optional[str]:
        try:
            import base64
            from app.services.llm_service import llm_service

            with open(file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            
            ext = os.path.splitext(file_path)[1].lower()
            mime = "image/png"
            if ext in (".jpg", ".jpeg"):
                mime = "image/jpeg"
            elif ext == ".gif":
                mime = "image/gif"
                
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "You are an OCR engine. Extract all text "
                                "from the uploaded image verbatim. "
                                "Do not add any preamble, conversational text, "
                                "or markdown formatting. Just output the extracted text."
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime};base64,{encoded_string}"
                            }
                        }
                    ]
                }
            ]
            
            ocr_text = llm_service.generate(messages=messages)
            return ocr_text.strip()
        except Exception as e:
            logger.error(f"Failed to extract text from image via LLM: {e}")
            return None

    def create_folder(self, user_id: uuid.UUID, name: str) -> DocumentFolder:
        db = SessionLocal()
        try:
            folder = DocumentFolder(user_id=user_id, name=name)
            db.add(folder)
            db.commit()
            db.refresh(folder)
            return folder
        finally:
            db.close()

    def get_user_folders(self, user_id: uuid.UUID) -> List[DocumentFolder]:
        db = SessionLocal()
        try:
            return db.query(DocumentFolder).filter(DocumentFolder.user_id == user_id).all()
        finally:
            db.close()

    def delete_folder(self, folder_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        db = SessionLocal()
        try:
            folder = db.query(DocumentFolder).filter(
                DocumentFolder.id == folder_id,
                DocumentFolder.user_id == user_id
            ).first()
            if not folder:
                return False
                
            # Documents cascade delete in DB, but we should remove files
            for doc in folder.documents:
                if os.path.exists(doc.file_path):
                    os.remove(doc.file_path)
                    
            db.delete(folder)
            db.commit()
            return True
        finally:
            db.close()

    async def upload_document(
        self, folder_id: uuid.UUID, user_id: uuid.UUID, file: UploadFile
    ) -> Optional[Document]:
        db = SessionLocal()
        try:
            # Verify folder belongs to user
            folder = db.query(DocumentFolder).filter(
                DocumentFolder.id == folder_id,
                DocumentFolder.user_id == user_id
            ).first()
            
            if not folder:
                return None
                
            user_dir = os.path.join(STORAGE_DIR, str(user_id))
            folder_dir = os.path.join(user_dir, str(folder_id))
            os.makedirs(folder_dir, exist_ok=True)
            
            file_ext = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(folder_dir, unique_filename)
            
            # Save file
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
                
            file_size = len(content)
            
            # Extract text based on file type
            ocr_text = None
            if file.content_type == "application/pdf" or file_ext.lower() == ".pdf":
                ocr_text = self.extract_text_from_pdf(file_path)
            elif file.content_type in ("image/png", "image/jpeg", "image/jpg") or file_ext.lower() in (".png", ".jpg", ".jpeg"):
                ocr_text = self.extract_text_from_image(file_path)
                
            document = Document(
                folder_id=folder_id,
                filename=file.filename,
                file_path=file_path,
                file_type=file.content_type,
                file_size=file_size,
                ocr_text=ocr_text,
            )
            
            db.add(document)
            db.commit()
            db.refresh(document)
            
            return document
        finally:
            db.close()

    def get_documents_in_folder(
        self, folder_id: uuid.UUID, user_id: uuid.UUID
    ) -> List[Document]:
        db = SessionLocal()
        try:
            folder = db.query(DocumentFolder).filter(
                DocumentFolder.id == folder_id,
                DocumentFolder.user_id == user_id
            ).first()
            if not folder:
                return []
            return folder.documents
        finally:
            db.close()

    def delete_document(self, document_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        db = SessionLocal()
        try:
            # We need to ensure document belongs to user
            doc = db.query(Document).join(DocumentFolder).filter(
                Document.id == document_id,
                DocumentFolder.user_id == user_id
            ).first()
            
            if not doc:
                return False
                
            if os.path.exists(doc.file_path):
                os.remove(doc.file_path)
                
            db.delete(doc)
            db.commit()
            return True
        finally:
            db.close()
            
    def get_document(self, document_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Document]:
        db = SessionLocal()
        try:
            return db.query(Document).join(DocumentFolder).filter(
                Document.id == document_id,
                DocumentFolder.user_id == user_id
            ).first()
        finally:
            db.close()

document_service = DocumentService()
