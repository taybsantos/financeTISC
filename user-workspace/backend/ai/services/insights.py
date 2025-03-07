from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.transaction import Transaction, TransactionType
from backend.models.asset import Asset, AssetType
from backend.models.debt import Debt, DebtStatus

def analyze_spending_patterns(db: Session, user_id: str, days: int = 30) -> Dict:
    """Analyze spending patterns and trends."""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get expenses grouped by category
    expenses = (
        db.query(
            Transaction.category_id,
            func.sum(Transaction.amount).label('total_amount')
        )
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.transaction_date >= start_date
        )
        .group_by(Transaction.category_id)
        .all()
    )
    
    # Calculate total expenses
    total_expenses = sum(expense.total_amount for expense in expenses)
    
    # Calculate category percentages
    category_breakdown = [
        {
            'category_id': expense.category_id,
            'amount': expense.total_amount,
            'percentage': (expense.total_amount / total_expenses * 100) if total_expenses > 0 else 0
        }
        for expense in expenses
    ]
    
    return {
        'total_expenses': total_expenses,
        'category_breakdown': category_breakdown,
        'daily_average': total_expenses / days if days > 0 else 0
    }

def analyze_income_sources(db: Session, user_id: str, months: int = 12) -> Dict:
    """Analyze income sources and trends."""
    start_date = datetime.utcnow() - timedelta(days=months*30)
    
    # Get income grouped by source
    incomes = (
        db.query(
            Transaction.source_account,
            func.sum(Transaction.amount).label('total_amount'),
            func.count(Transaction.id).label('frequency')
        )
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.INCOME,
            Transaction.transaction_date >= start_date
        )
        .group_by(Transaction.source_account)
        .all()
    )
    
    total_income = sum(income.total_amount for income in incomes)
    
    return {
        'total_income': total_income,
        'monthly_average': total_income / months if months > 0 else 0,
        'sources': [
            {
                'source': income.source_account,
                'amount': income.total_amount,
                'frequency': income.frequency,
                'percentage': (income.total_amount / total_income * 100) if total_income > 0 else 0
            }
            for income in incomes
        ]
    }

def analyze_asset_allocation(db: Session, user_id: str) -> Dict:
    """Analyze asset allocation and diversification."""
    assets = (
        db.query(
            Asset.type,
            func.sum(Asset.current_value).label('total_value')
        )
        .filter(Asset.user_id == user_id)
        .group_by(Asset.type)
        .all()
    )
    
    total_value = sum(asset.total_value for asset in assets)
    
    allocation = [
        {
            'type': asset.type,
            'value': asset.total_value,
            'percentage': (asset.total_value / total_value * 100) if total_value > 0 else 0
        }
        for asset in assets
    ]
    
    # Calculate diversification score (0-100)
    num_types = len(assets)
    max_percentage = max(asset.total_value / total_value * 100 for asset in assets) if total_value > 0 else 100
    diversification_score = min(100, (num_types * 20) * (100 - max_percentage) / 100)
    
    return {
        'total_value': total_value,
        'allocation': allocation,
        'diversification_score': diversification_score
    }

def analyze_debt_health(db: Session, user_id: str) -> Dict:
    """Analyze debt health and provide recommendations."""
    debts = (
        db.query(Debt)
        .filter(
            Debt.user_id == user_id,
            Debt.status != DebtStatus.PAID_OFF
        )
        .all()
    )
    
    total_debt = sum(debt.current_balance for debt in debts)
    total_monthly_payment = sum(debt.payment_amount for debt in debts)
    
    # Calculate weighted average interest rate
    if total_debt > 0:
        avg_interest_rate = sum(
            debt.interest_rate * (debt.current_balance / total_debt)
            for debt in debts
        )
    else:
        avg_interest_rate = 0
    
    # Analyze each debt
    debt_analysis = []
    for debt in debts:
        months_to_payoff = (
            debt.current_balance / debt.payment_amount
            if debt.payment_amount and debt.payment_amount > 0
            else float('inf')
        )
        
        total_interest = (
            debt.current_balance * (debt.interest_rate / 100) * (months_to_payoff / 12)
            if months_to_payoff != float('inf')
            else None
        )
        
        debt_analysis.append({
            'id': debt.id,
            'name': debt.name,
            'current_balance': debt.current_balance,
            'interest_rate': debt.interest_rate,
            'monthly_payment': debt.payment_amount,
            'months_to_payoff': months_to_payoff if months_to_payoff != float('inf') else None,
            'total_interest': total_interest
        })
    
    # Sort debts by interest rate for debt avalanche method
    avalanche_order = sorted(
        debt_analysis,
        key=lambda x: x['interest_rate'],
        reverse=True
    )
    
    # Sort debts by balance for debt snowball method
    snowball_order = sorted(
        debt_analysis,
        key=lambda x: x['current_balance']
    )
    
    return {
        'total_debt': total_debt,
        'total_monthly_payment': total_monthly_payment,
        'average_interest_rate': avg_interest_rate,
        'debt_analysis': debt_analysis,
        'recommendations': {
            'avalanche_method': [debt['id'] for debt in avalanche_order],
            'snowball_method': [debt['id'] for debt in snowball_order]
        }
    }

def generate_financial_insights(db: Session, user_id: str) -> Dict:
    """Generate comprehensive financial insights and recommendations."""
    spending = analyze_spending_patterns(db, user_id)
    income = analyze_income_sources(db, user_id)
    assets = analyze_asset_allocation(db, user_id)
    debt = analyze_debt_health(db, user_id)
    
    # Calculate key financial ratios
    monthly_income = income['monthly_average']
    monthly_expenses = spending['daily_average'] * 30
    debt_payments = debt['total_monthly_payment']
    
    savings_rate = ((monthly_income - monthly_expenses) / monthly_income * 100) if monthly_income > 0 else 0
    debt_to_income = (debt_payments / monthly_income * 100) if monthly_income > 0 else 0
    net_worth = assets['total_value'] - debt['total_debt']
    
    return {
        'summary': {
            'net_worth': net_worth,
            'monthly_income': monthly_income,
            'monthly_expenses': monthly_expenses,
            'savings_rate': savings_rate,
            'debt_to_income_ratio': debt_to_income
        },
        'spending_analysis': spending,
        'income_analysis': income,
        'asset_analysis': assets,
        'debt_analysis': debt,
        'recommendations': generate_recommendations(
            savings_rate=savings_rate,
            debt_to_income=debt_to_income,
            diversification_score=assets['diversification_score'],
            avg_interest_rate=debt['average_interest_rate']
        )
    }

def generate_recommendations(
    savings_rate: float,
    debt_to_income: float,
    diversification_score: float,
    avg_interest_rate: float
) -> List[Dict]:
    """Generate personalized financial recommendations."""
    recommendations = []
    
    # Savings recommendations
    if savings_rate < 20:
        recommendations.append({
            'category': 'savings',
            'priority': 'high',
            'title': 'Increase Savings Rate',
            'description': 'Aim to save at least 20% of your monthly income. Review expenses to find areas where you can cut back.'
        })
    
    # Debt recommendations
    if debt_to_income > 43:
        recommendations.append({
            'category': 'debt',
            'priority': 'high',
            'title': 'Reduce Debt-to-Income Ratio',
            'description': 'Your debt-to-income ratio is high. Consider debt consolidation or accelerated debt repayment strategies.'
        })
    
    if avg_interest_rate > 15:
        recommendations.append({
            'category': 'debt',
            'priority': 'medium',
            'title': 'High Interest Debt',
            'description': 'Consider refinancing high-interest debt or transferring credit card balances to lower-interest options.'
        })
    
    # Investment recommendations
    if diversification_score < 60:
        recommendations.append({
            'category': 'investment',
            'priority': 'medium',
            'title': 'Improve Portfolio Diversification',
            'description': 'Your investment portfolio could benefit from better diversification across different asset types.'
        })
    
    return recommendations
