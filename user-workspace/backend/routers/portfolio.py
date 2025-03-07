from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from backend.config.database import get_db
from backend.models.user import User
from backend.models.asset import Asset, AssetType, AssetStatus
from backend.models.debt import Debt, DebtType, DebtStatus
from backend.routers.auth import get_current_user
from backend.ai.services.reports import FinancialReportService
from backend.ai.services.projections import FinancialProjectionService

router = APIRouter(prefix="/portfolio", tags=["portfolio"])
report_service = FinancialReportService()
projection_service = FinancialProjectionService()

# Asset routes
@router.post("/assets", response_model=dict)
async def create_asset(
    asset_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new asset."""
    asset = Asset(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        **asset_data
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset.to_dict()

@router.get("/assets", response_model=List[dict])
async def get_assets(
    asset_type: Optional[AssetType] = None,
    status: Optional[AssetStatus] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's assets with optional filtering."""
    query = db.query(Asset).filter(Asset.user_id == current_user.id)
    
    if asset_type:
        query = query.filter(Asset.type == asset_type)
    if status:
        query = query.filter(Asset.status == status)
        
    assets = query.all()
    return [asset.to_dict() for asset in assets]

@router.get("/assets/{asset_id}", response_model=dict)
async def get_asset(
    asset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific asset details."""
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.user_id == current_user.id
    ).first()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
        
    return asset.to_dict()

@router.put("/assets/{asset_id}", response_model=dict)
async def update_asset(
    asset_id: str,
    asset_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update asset details."""
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.user_id == current_user.id
    ).first()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
        
    for key, value in asset_data.items():
        setattr(asset, key, value)
        
    db.commit()
    db.refresh(asset)
    return asset.to_dict()

@router.delete("/assets/{asset_id}")
async def delete_asset(
    asset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an asset."""
    asset = db.query(Asset).filter(
        Asset.id == asset_id,
        Asset.user_id == current_user.id
    ).first()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
        
    db.delete(asset)
    db.commit()
    return {"message": "Asset deleted successfully"}

# Debt routes
@router.post("/debts", response_model=dict)
async def create_debt(
    debt_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new debt."""
    debt = Debt(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        **debt_data
    )
    db.add(debt)
    db.commit()
    db.refresh(debt)
    return debt.to_dict()

@router.get("/debts", response_model=List[dict])
async def get_debts(
    debt_type: Optional[DebtType] = None,
    status: Optional[DebtStatus] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's debts with optional filtering."""
    query = db.query(Debt).filter(Debt.user_id == current_user.id)
    
    if debt_type:
        query = query.filter(Debt.type == debt_type)
    if status:
        query = query.filter(Debt.status == status)
        
    debts = query.all()
    return [debt.to_dict() for debt in debts]

@router.get("/debts/{debt_id}", response_model=dict)
async def get_debt(
    debt_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific debt details."""
    debt = db.query(Debt).filter(
        Debt.id == debt_id,
        Debt.user_id == current_user.id
    ).first()
    
    if not debt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Debt not found"
        )
        
    return debt.to_dict()

@router.put("/debts/{debt_id}", response_model=dict)
async def update_debt(
    debt_id: str,
    debt_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update debt details."""
    debt = db.query(Debt).filter(
        Debt.id == debt_id,
        Debt.user_id == current_user.id
    ).first()
    
    if not debt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Debt not found"
        )
        
    for key, value in debt_data.items():
        setattr(debt, key, value)
        
    db.commit()
    db.refresh(debt)
    return debt.to_dict()

@router.delete("/debts/{debt_id}")
async def delete_debt(
    debt_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a debt."""
    debt = db.query(Debt).filter(
        Debt.id == debt_id,
        Debt.user_id == current_user.id
    ).first()
    
    if not debt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Debt not found"
        )
        
    db.delete(debt)
    db.commit()
    return {"message": "Debt deleted successfully"}

# Portfolio analysis routes
@router.get("/analysis/net-worth")
async def get_net_worth(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current net worth analysis."""
    assets = db.query(Asset).filter(Asset.user_id == current_user.id).all()
    debts = db.query(Debt).filter(Debt.user_id == current_user.id).all()
    
    total_assets = sum(asset.calculate_current_value() for asset in assets)
    total_debts = sum(debt.current_balance for debt in debts)
    
    return {
        "total_assets": total_assets,
        "total_debts": total_debts,
        "net_worth": total_assets - total_debts,
        "asset_breakdown": {
            asset_type.value: sum(
                asset.calculate_current_value() 
                for asset in assets 
                if asset.type == asset_type
            )
            for asset_type in AssetType
        },
        "debt_breakdown": {
            debt_type.value: sum(
                debt.current_balance 
                for debt in debts 
                if debt.type == debt_type
            )
            for debt_type in DebtType
        },
        "timestamp": datetime.now().isoformat()
    }

@router.get("/analysis/projections")
async def get_portfolio_projections(
    months_ahead: int = 12,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get portfolio projections."""
    assets = db.query(Asset).filter(Asset.user_id == current_user.id).all()
    debts = db.query(Debt).filter(Debt.user_id == current_user.id).all()
    
    return projection_service.generate_net_worth_projection(
        assets=[asset.to_dict() for asset in assets],
        debts=[debt.to_dict() for debt in debts],
        months_ahead=months_ahead
    )

@router.get("/analysis/debt-overview")
async def get_debt_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive debt overview."""
    debts = db.query(Debt).filter(Debt.user_id == current_user.id).all()
    
    total_debt = sum(debt.current_balance for debt in debts)
    monthly_payments = sum(debt.payment_amount for debt in debts)
    weighted_avg_rate = sum(
        debt.current_balance * debt.interest_rate 
        for debt in debts
    ) / total_debt if total_debt > 0 else 0
    
    return {
        "total_debt": total_debt,
        "monthly_payments": monthly_payments,
        "average_interest_rate": weighted_avg_rate,
        "debt_types": {
            debt_type.value: sum(
                debt.current_balance 
                for debt in debts 
                if debt.type == debt_type
            )
            for debt_type in DebtType
        },
        "past_due_amount": sum(
            debt.current_balance 
            for debt in debts 
            if debt.is_past_due()
        ),
        "debt_status": {
            status.value: sum(
                debt.current_balance 
                for debt in debts 
                if debt.status == status
            )
            for status in DebtStatus
        },
        "timestamp": datetime.now().isoformat()
    }
