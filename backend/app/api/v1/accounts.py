from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
from datetime import datetime
from app.core.database import get_db
from app.core.security import encrypt_credentials, decrypt_credentials
from app.models.user import User
from app.models.project import Project
from app.models.account_connection import AccountConnection, ConnectionStatus
from app.schemas.account import AccountConnectionCreate, AccountConnectionResponse
from app.api.v1.dependencies import get_current_user
from app.services.account_service import test_connection
import json

router = APIRouter()

@router.post("/", response_model=AccountConnectionResponse)
async def create_account_connection(
    account_data: AccountConnectionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify project ownership
    result = await db.execute(
        select(Project).where(Project.id == account_data.project_id, Project.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Test connection
    is_valid = await test_connection(account_data.service_type, account_data.credentials)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Connection test failed")
    
    # Encrypt and store
    encrypted_creds = encrypt_credentials(json.dumps(account_data.credentials))
    account = AccountConnection(
        project_id=account_data.project_id,
        service_type=account_data.service_type,
        credentials_encrypted=encrypted_creds,
        config=account_data.config,
        status=ConnectionStatus.active,
        last_tested=datetime.utcnow()
    )
    
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account

@router.get("/project/{project_id}", response_model=List[AccountConnectionResponse])
async def get_project_accounts(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify project ownership
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")
    
    result = await db.execute(
        select(AccountConnection).where(AccountConnection.project_id == project_id)
    )
    return result.scalars().all()

@router.delete("/{account_id}")
async def delete_account(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(AccountConnection).where(AccountConnection.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Verify ownership through project
    result = await db.execute(
        select(Project).where(Project.id == account.project_id, Project.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Access denied")
    
    await db.delete(account)
    await db.commit()
    return {"message": "Account deleted successfully"}