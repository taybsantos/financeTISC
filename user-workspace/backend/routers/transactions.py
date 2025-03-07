from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel, constr
from decimal import Decimal

from backend.config.database import get_db
from backend.models.transaction import Transaction, TransactionType, TransactionStatus
from backend.models.user import User, Category
from backend.routers.auth import get_current_user

router = APIRouter(prefix="/transactions", tags=["transactions"])

# Pydantic models
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class TransactionBase(BaseModel):
    amount: Decimal
    description: Optional[str] = None
    type: TransactionType
    category_id: Optional[str] = None
    transaction_date: date
    source_account: Optional[str] = None
    destination_account: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    type: Optional[TransactionType] = None
    category_id: Optional[str] = None
    status: Optional[TransactionStatus] = None
    transaction_date: Optional[date] = None
    source_account: Optional[str] = None
    destination_account: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

class TransactionResponse(TransactionBase):
    id: str
    user_id: str
    status: TransactionStatus
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None

    class Config:
        orm_mode = True

# Routes
@router.post("/categories", response_model=CategoryResponse)
async def create_category(
    category: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_category = Category(**category.dict(), user_id=current_user.id)
    db.add(db_category)
    try:
        db.commit()
        db.refresh(db_category)
        return db_category
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating category"
        )

@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Category).filter(Category.user_id == current_user.id).all()

@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate category if provided
    if transaction.category_id:
        category = db.query(Category).filter(
            Category.id == transaction.category_id,
            Category.user_id == current_user.id
        ).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

    # Create transaction
    db_transaction = Transaction(
        **transaction.dict(),
        user_id=current_user.id,
        tags=','.join(transaction.tags) if transaction.tags else None
    )
    
    db.add(db_transaction)
    try:
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating transaction"
        )

@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    transaction_type: Optional[TransactionType] = None,
    category_id: Optional[str] = None,
    status: Optional[TransactionStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)
    
    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)
    if transaction_type:
        query = query.filter(Transaction.type == transaction_type)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if status:
        query = query.filter(Transaction.status == status)
    
    return query.order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).all()

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return transaction

@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    transaction_update: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    
    if not db_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Update transaction fields
    update_data = transaction_update.dict(exclude_unset=True)
    if 'tags' in update_data:
        update_data['tags'] = ','.join(update_data['tags']) if update_data['tags'] else None
    
    for field, value in update_data.items():
        setattr(db_transaction, field, value)
    
    try:
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating transaction"
        )

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    try:
        db.delete(transaction)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting transaction"
        )
