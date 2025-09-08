"""
Asset management endpoints.
"""

import hashlib
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from app.core.database import get_db
from app.core.aifs_client import AIFSClientManager
from app.core.exceptions import AssetNotFoundError, InvalidFileTypeError, FileTooLargeError
from app.models.asset import Asset as AssetModel
from app.schemas.asset import (
    Asset, AssetCreate, AssetUpdate, AssetUpload, AssetListResponse,
    AssetSearchQuery, AssetSearchResponse
)
from app.services.asset_service import AssetService
from app.services.embedding_service import EmbeddingService

router = APIRouter()


def get_asset_service(
    db: Session = Depends(get_db),
    aifs_manager: AIFSClientManager = Depends(lambda: AIFSClientManager())
) -> AssetService:
    """Get asset service instance."""
    return AssetService(db, aifs_manager)


@router.get("/", response_model=AssetListResponse)
async def list_assets(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort: str = Query("created_at"),
    order: str = Query("desc"),
    type: Optional[str] = None,
    tags: Optional[str] = None,
    search: Optional[str] = None,
    asset_service: AssetService = Depends(get_asset_service)
):
    """List assets with pagination and filtering."""
    try:
        # Parse tags if provided
        tag_list = tags.split(",") if tags else None
        
        # Get sort order
        sort_order = desc if order == "desc" else asc
        
        assets, total = await asset_service.list_assets(
            page=page,
            per_page=per_page,
            sort=sort,
            sort_order=sort_order,
            asset_type=type,
            tags=tag_list,
            search=search
        )
        
        pages = (total + per_page - 1) // per_page
        
        return AssetListResponse(
            assets=assets,
            total=total,
            page=page,
            per_page=per_page,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{asset_id}", response_model=Asset)
async def get_asset(
    asset_id: str,
    asset_service: AssetService = Depends(get_asset_service)
):
    """Get asset by ID."""
    try:
        asset = await asset_service.get_asset(asset_id)
        if not asset:
            raise AssetNotFoundError(asset_id)
        return asset
    except AssetNotFoundError:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=Asset)
async def upload_asset(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    parents: Optional[str] = Form(None),
    generate_embedding: bool = Form(True),
    asset_service: AssetService = Depends(get_asset_service)
):
    """Upload a new asset."""
    try:
        # Validate file type
        if file.content_type not in asset_service.allowed_file_types:
            raise InvalidFileTypeError(
                file.content_type,
                asset_service.allowed_file_types
            )
        
        # Validate file size
        if file.size and file.size > asset_service.max_file_size:
            raise FileTooLargeError(file.size, asset_service.max_file_size)
        
        # Read file content
        content = await file.read()
        
        # Generate content hash
        content_hash = hashlib.sha256(content).hexdigest()
        
        # Parse optional parameters
        import json
        metadata_dict = json.loads(metadata) if metadata else None
        tag_list = tags.split(",") if tags else None
        parent_list = parents.split(",") if parents else None
        
        # Create asset
        asset_data = AssetCreate(
            name=name or file.filename,
            type="file",
            mime_type=file.content_type,
            size=len(content),
            content_hash=content_hash,
            metadata=metadata_dict,
            tags=tag_list,
            parents=[{"asset_id": pid} for pid in parent_list] if parent_list else None
        )
        
        asset = await asset_service.create_asset(asset_data, content, generate_embedding)
        return asset
        
    except (InvalidFileTypeError, FileTooLargeError):
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=Asset)
async def create_asset(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    parents: Optional[str] = Form(None),
    generate_embedding: bool = Form(True),
    asset_service: AssetService = Depends(get_asset_service)
):
    """Create a new asset (alias for upload)."""
    return await upload_asset(file, name, metadata, tags, parents, generate_embedding, asset_service)


@router.put("/{asset_id}", response_model=Asset)
async def update_asset(
    asset_id: str,
    asset_update: AssetUpdate,
    asset_service: AssetService = Depends(get_asset_service)
):
    """Update an asset."""
    try:
        asset = await asset_service.update_asset(asset_id, asset_update)
        if not asset:
            raise AssetNotFoundError(asset_id)
        return asset
    except AssetNotFoundError:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: str,
    asset_service: AssetService = Depends(get_asset_service)
):
    """Delete an asset."""
    try:
        success = await asset_service.delete_asset(asset_id)
        if not success:
            raise AssetNotFoundError(asset_id)
        return {"message": "Asset deleted successfully"}
    except AssetNotFoundError:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{asset_id}/download")
async def download_asset(
    asset_id: str,
    asset_service: AssetService = Depends(get_asset_service)
):
    """Download an asset."""
    try:
        asset_data = await asset_service.download_asset(asset_id)
        if not asset_data:
            raise AssetNotFoundError(asset_id)
        
        from fastapi.responses import StreamingResponse
        import io
        
        return StreamingResponse(
            io.BytesIO(asset_data["content"]),
            media_type=asset_data["mime_type"],
            headers={"Content-Disposition": f"attachment; filename={asset_data['name']}"}
        )
    except AssetNotFoundError:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def batch_upload(
    files: List[UploadFile] = File(...),
    metadata: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    generate_embeddings: bool = Form(True),
    asset_service: AssetService = Depends(get_asset_service)
):
    """Batch upload multiple assets."""
    try:
        import json
        metadata_dict = json.loads(metadata) if metadata else None
        tag_list = tags.split(",") if tags else None
        
        results = []
        for file in files:
            try:
                # Validate file type
                if file.content_type not in asset_service.allowed_file_types:
                    results.append({
                        "filename": file.filename,
                        "status": "error",
                        "error": f"Invalid file type: {file.content_type}"
                    })
                    continue
                
                # Read file content
                content = await file.read()
                
                # Generate content hash
                content_hash = hashlib.sha256(content).hexdigest()
                
                # Create asset
                asset_data = AssetCreate(
                    name=file.filename,
                    type="file",
                    mime_type=file.content_type,
                    size=len(content),
                    content_hash=content_hash,
                    metadata=metadata_dict,
                    tags=tag_list
                )
                
                asset = await asset_service.create_asset(asset_data, content, generate_embeddings)
                results.append({
                    "filename": file.filename,
                    "status": "success",
                    "asset_id": asset.id
                })
                
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "upload_id": str(uuid.uuid4()),
            "results": results,
            "total_files": len(files),
            "successful": len([r for r in results if r["status"] == "success"]),
            "failed": len([r for r in results if r["status"] == "error"])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
