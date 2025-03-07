from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd

from backend.models.transaction import Transaction, TransactionType
from backend.models.asset import Asset, AssetType
from backend.models.debt import Debt, DebtStatus
from backend.ai.services.insights import (
    analyze_spending_patterns,
    analyze_income_sources,
    analyze_asset_allocation,
    analyze_debt_health
)

def generate_monthly_report(db: Session, user_id: str, month: int, year: int) -> Dict:
    """Generate a comprehensive monthly financial report."""
    start_date = datetime(year, month, 1)
    end_date = (start_date + timedelta(days=32)).replace(day=1)
    
    # Get transactions for the month
    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date < end_date
        )
        .all()
    )
    
    # Calculate income and expenses
    income = sum(t.amount for t in transactions if t.type == TransactionType.INCOME)
    expenses = sum(t.amount for t in transactions if t.type == TransactionType.EXPENSE)
    net_income = income - expenses
    
    # Get spending patterns
    spending = analyze_spending_patterns(db, user_id, days=30)
    
    # Get asset and debt snapshots
    assets = analyze_asset_allocation(db, user_id)
    debts = analyze_debt_health(db, user_id)
    
    return {
        "period": {
            "month": month,
            "year": year,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "summary": {
            "total_income": income,
            "total_expenses": expenses,
            "net_income": net_income,
            "savings_rate": (net_income / income * 100) if income > 0 else 0
        },
        "spending_breakdown": spending["category_breakdown"],
        "assets": {
            "total_value": assets["total_value"],
            "allocation": assets["allocation"]
        },
        "debts": {
            "total_debt": debts["total_debt"],
            "monthly_payment": debts["total_monthly_payment"]
        }
    }

def generate_annual_report(db: Session, user_id: str, year: int) -> Dict:
    """Generate a comprehensive annual financial report."""
    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)
    
    # Get all transactions for the year
    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == user_id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date < end_date
        )
        .all()
    )
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame([
        {
            'amount': t.amount,
            'type': t.type,
            'category_id': t.category_id,
            'date': t.transaction_date,
            'month': t.transaction_date.month
        }
        for t in transactions
    ])
    
    # Monthly breakdown
    monthly_summary = []
    for month in range(1, 13):
        month_data = df[df['month'] == month]
        income = month_data[month_data['type'] == TransactionType.INCOME]['amount'].sum()
        expenses = month_data[month_data['type'] == TransactionType.EXPENSE]['amount'].sum()
        
        monthly_summary.append({
            'month': month,
            'income': income,
            'expenses': expenses,
            'net_income': income - expenses
        })
    
    # Calculate year totals
    total_income = sum(m['income'] for m in monthly_summary)
    total_expenses = sum(m['expenses'] for m in monthly_summary)
    net_income = total_income - total_expenses
    
    # Get current asset and debt status
    assets = analyze_asset_allocation(db, user_id)
    debts = analyze_debt_health(db, user_id)
    
    return {
        "period": {
            "year": year,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "summary": {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_income": net_income,
            "savings_rate": (net_income / total_income * 100) if total_income > 0 else 0,
            "average_monthly_income": total_income / 12,
            "average_monthly_expenses": total_expenses / 12
        },
        "monthly_breakdown": monthly_summary,
        "assets": {
            "total_value": assets["total_value"],
            "allocation": assets["allocation"],
            "diversification_score": assets["diversification_score"]
        },
        "debts": {
            "total_debt": debts["total_debt"],
            "monthly_payment": debts["total_monthly_payment"],
            "average_interest_rate": debts["average_interest_rate"]
        },
        "recommendations": generate_report_recommendations(
            net_income=net_income,
            total_income=total_income,
            assets=assets,
            debts=debts
        )
    }

def generate_tax_report(db: Session, user_id: str, year: int) -> Dict:
    """Generate a tax-focused financial report."""
    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)
    
    # Get all income transactions
    income_transactions = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.INCOME,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date < end_date
        )
        .all()
    )
    
    # Group income by source
    income_sources = {}
    for t in income_transactions:
        source = t.source_account or "Other"
        if source not in income_sources:
            income_sources[source] = 0
        income_sources[source] += t.amount
    
    # Get tax-deductible expenses
    deductible_expenses = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date < end_date,
            # Add filters for tax-deductible categories
        )
        .all()
    )
    
    # Calculate capital gains from assets
    assets = (
        db.query(Asset)
        .filter(Asset.user_id == user_id)
        .all()
    )
    
    capital_gains = sum(
        (asset.current_value - asset.acquisition_value)
        for asset in assets
        if asset.acquisition_date and asset.acquisition_date.year == year
        and asset.current_value and asset.acquisition_value
    )
    
    return {
        "year": year,
        "income": {
            "sources": income_sources,
            "total": sum(income_sources.values())
        },
        "deductions": {
            "expenses": [
                {
                    "category": t.category_id,
                    "amount": t.amount,
                    "description": t.description
                }
                for t in deductible_expenses
            ],
            "total": sum(t.amount for t in deductible_expenses)
        },
        "capital_gains": capital_gains
    }

def generate_report_recommendations(
    net_income: float,
    total_income: float,
    assets: Dict,
    debts: Dict
) -> List[Dict]:
    """Generate recommendations based on annual report data."""
    recommendations = []
    
    # Savings recommendations
    savings_rate = (net_income / total_income * 100) if total_income > 0 else 0
    if savings_rate < 20:
        recommendations.append({
            "category": "savings",
            "priority": "high",
            "title": "Increase Savings Rate",
            "description": f"Your current savings rate is {savings_rate:.1f}%. Consider setting a goal to save at least 20% of your income."
        })
    
    # Asset allocation recommendations
    if assets["diversification_score"] < 70:
        recommendations.append({
            "category": "investments",
            "priority": "medium",
            "title": "Diversify Investment Portfolio",
            "description": "Your portfolio could benefit from better diversification across different asset classes."
        })
    
    # Debt recommendations
    if debts["average_interest_rate"] > 10:
        recommendations.append({
            "category": "debt",
            "priority": "high",
            "title": "Address High-Interest Debt",
            "description": "Consider consolidating or refinancing your high-interest debt to reduce interest expenses."
        })
    
    return recommendations
