from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import uuid4

from backend.config.database import get_db
from backend.models.asset import Asset, AssetType, AssetStatus
from backend.models.debt import Debt, DebtType, DebtStatus, PaymentFrequency
from backend.models.user import User
from backend.routers.auth import get_current_user

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

# Asset endpoints
@router.post("/assets", response_model=dict)
async def create_asset(
    asset_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new asset."""
    asset = Asset(
        id=str(uuid4()),
        user_id=current_user.id,
        **asset_data
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset

@router.get("/assets", response_model=List[dict])
async def get_assets(
    type: Optional[AssetType] = None,
    status: Optional[AssetStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all assets for the current user."""
    query = db.query(Asset).filter(Asset.user_id == current_user.id)
    if type:
        query = query.filter(Asset.type == type)
    if status:
        query = query.filter(Asset.status == status)
    return query.all()

@router.get("/assets/{asset_id}", response_model=dict)
async def get_asset(
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific asset."""
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.user_id == current_user.id
    ).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@router.put("/assets/{asset_id}", response_model=dict)
async def update_asset(
    asset_id: str,
    asset_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an asset."""
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.user_id == current_user.id
    ).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    for key, value in asset_data.items():
        setattr(asset, key, value)
    
    db.commit()
    db.refresh(asset)
    return asset

@router.delete("/assets/{asset_id}")
async def delete_asset(
    asset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an asset."""
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.user_id == current_user.id
    ).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    db.delete(asset)
    db.commit()
    return {"message": "Asset deleted"}

# Debt endpoints
@router.post("/debts", response_model=dict)
async def create_debt(
    debt_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new debt."""
    debt = Debt(
        id=str(uuid4()),
        user_id=current_user.id,
        **debt_data
    )
    db.add(debt)
    db.commit()
    db.refresh(debt)
    return debt

@router.get("/debts", response_model=List[dict])
async def get_debts(
    type: Optional[DebtType] = None,
    status: Optional[DebtStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all debts for the current user."""
    query = db.query(Debt).filter(Debt.user_id == current_user.id)
    if type:
        query = query.filter(Debt.type == type)
    if status:
        query = query.filter(Debt.status == status)
    return query.all()

@router.get("/debts/{debt_id}", response_model=dict)
async def get_debt(
    debt_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific debt."""
    debt = db.query(Debt).filter(
        Debt.id == debt_id,
        Debt.user_id == current_user.id
    ).first()
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    return debt

@router.put("/debts/{debt_id}", response_model=dict)
async def update_debt(
    debt_id: str,
    debt_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a debt."""
    debt = db.query(Debt).filter(
        Debt.id == debt_id,
        Debt.user_id == current_user.id
    ).first()
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    
    for key, value in debt_data.items():
        setattr(debt, key, value)
    
    db.commit()
    db.refresh(debt)
    return debt

@router.delete("/debts/{debt_id}")
async def delete_debt(
    debt_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a debt."""
    debt = db.query(Debt).filter(
        Debt.id == debt_id,
        Debt.user_id == current_user.id
    ).first()
    if not debt:
        raise HTTPException(status_code=404, detail="Debt not found")
    
    db.delete(debt)
    db.commit()
    return {"message": "Debt deleted"}

# Analysis endpoints
@router.get("/analysis/net-worth")
async def get_net_worth(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate net worth (total assets - total debts)."""
    total_assets = db.query(Asset).filter(
        Asset.user_id == current_user.id,
        Asset.status != AssetStatus.SOLD
    ).with_entities(db.func.sum(Asset.current_value)).scalar() or 0

    total_debts = db.query(Debt).filter(
        Debt.user_id == current_user.id,
        Debt.status != DebtStatus.PAID_OFF
    ).with_entities(db.func.sum(Debt.current_balance)).scalar() or 0

    return {
        "total_assets": total_assets,
        "total_debts": total_debts,
        "net_worth": total_assets - total_debts
    }

@router.get("/analysis/debt-overview")
async def get_debt_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get debt overview including total debt, monthly payments, etc."""
    debts = db.query(Debt).filter(
        Debt.user_id == current_user.id,
        Debt.status != DebtStatus.PAID_OFF
    ).all()

    total_debt = sum(debt.current_balance for debt in debts)
    monthly_payments = sum(debt.payment_amount for debt in debts if debt.payment_frequency == PaymentFrequency.MONTHLY)
    
    # Calculate average interest rate weighted by debt amount
    weighted_interest = sum(debt.interest_rate * debt.current_balance for debt in debts)
    average_interest_rate = weighted_interest / total_debt if total_debt > 0 else 0

    # Group debts by type
    debt_types = {}
    for debt in debts:
        if debt.type not in debt_types:
            debt_types[debt.type] = 0
        debt_types[debt.type] += debt.current_balance

    return {
        "total_debt": total_debt,
        "monthly_payments": monthly_payments,
        "average_interest_rate": average_interest_rate,
        "debt_types": debt_types
    }

@router.get("/analysis/projections")
async def get_portfolio_projections(
    months: int = Query(12, ge=1, le=120),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get portfolio projections for the specified number of months."""
    from backend.ai.services.projections import calculate_portfolio_projections
    
    assets = db.query(Asset).filter(
        Asset.user_id == current_user.id,
        Asset.status != AssetStatus.SOLD
    ).all()

    debts = db.query(Debt).filter(
        Debt.user_id == current_user.id,
        Debt.status != DebtStatus.PAID_OFF
    ).all()

    projections = calculate_portfolio_projections(assets, debts, months)
    
    return {
        "current_net_worth": projections["current_net_worth"],
        "monthly_projections": projections["monthly_projections"]
    }
