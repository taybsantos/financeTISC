from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.ai.services import (
    categorization,
    insights,
    projections,
    reports
)

router = APIRouter(prefix="/ai", tags=["ai"])

# Transaction Categorization Endpoints
@router.post("/categorize")
async def categorize_transaction(
    description: str,
    amount: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Automatically categorize a transaction based on its description."""
    result = categorization.categorize_transaction(
        db=db,
        user_id=current_user.id,
        description=description,
        amount=amount
    )
    return result

@router.post("/categorize/bulk")
async def categorize_transactions(
    transactions: List[dict],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Categorize multiple transactions in bulk."""
    results = categorization.bulk_categorize_transactions(
        db=db,
        user_id=current_user.id,
        transactions=transactions
    )
    return results

# Financial Insights Endpoints
@router.get("/insights/spending")
async def get_spending_insights(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get insights about spending patterns."""
    return insights.analyze_spending_patterns(
        db=db,
        user_id=current_user.id,
        days=days
    )

@router.get("/insights/income")
async def get_income_insights(
    months: int = Query(12, ge=1, le=60),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get insights about income sources and trends."""
    return insights.analyze_income_sources(
        db=db,
        user_id=current_user.id,
        months=months
    )

@router.get("/insights/assets")
async def get_asset_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get insights about asset allocation and diversification."""
    return insights.analyze_asset_allocation(
        db=db,
        user_id=current_user.id
    )

@router.get("/insights/debt")
async def get_debt_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get insights about debt health and recommendations."""
    return insights.analyze_debt_health(
        db=db,
        user_id=current_user.id
    )

@router.get("/insights/summary")
async def get_financial_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive financial insights and recommendations."""
    return insights.generate_financial_insights(
        db=db,
        user_id=current_user.id
    )

# Financial Projections Endpoints
@router.get("/projections/portfolio")
async def get_portfolio_projections(
    months: int = Query(12, ge=1, le=120),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get portfolio projections including assets and debts."""
    assets = db.query(Asset).filter(
        Asset.user_id == current_user.id,
        Asset.status != AssetStatus.SOLD
    ).all()

    debts = db.query(Debt).filter(
        Debt.user_id == current_user.id,
        Debt.status != DebtStatus.PAID_OFF
    ).all()

    return projections.calculate_portfolio_projections(
        assets=assets,
        debts=debts,
        months=months
    )

# Financial Reports Endpoints
@router.get("/reports/monthly")
async def get_monthly_report(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000, le=datetime.now().year),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a monthly financial report."""
    return reports.generate_monthly_report(
        db=db,
        user_id=current_user.id,
        month=month,
        year=year
    )

@router.get("/reports/annual")
async def get_annual_report(
    year: int = Query(..., ge=2000, le=datetime.now().year),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate an annual financial report."""
    return reports.generate_annual_report(
        db=db,
        user_id=current_user.id,
        year=year
    )

@router.get("/reports/tax")
async def get_tax_report(
    year: int = Query(..., ge=2000, le=datetime.now().year),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a tax-focused financial report."""
    return reports.generate_tax_report(
        db=db,
        user_id=current_user.id,
        year=year
    )
