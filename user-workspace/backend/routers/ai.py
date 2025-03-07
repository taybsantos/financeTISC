from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from backend.config.database import get_db
from backend.models.user import User
from backend.models.transaction import Transaction
from backend.routers.auth import get_current_user
from backend.ai.services.categorization import TransactionCategorizer
from backend.ai.services.insights import FinancialInsights

router = APIRouter(prefix="/ai", tags=["ai"])

# Initialize AI services
categorizer = TransactionCategorizer()
insights = FinancialInsights()

# Pydantic models for requests and responses
class CategoryPrediction(BaseModel):
    category: str
    confidence: float

class SpendingAnalysis(BaseModel):
    total_spending: float
    average_daily_spending: float
    category_analysis: Dict
    unusual_transactions: List[Dict]
    timestamp: str

class ForecastResponse(BaseModel):
    forecast: List[Dict]
    timestamp: str

class SavingsRecommendation(BaseModel):
    current_savings_rate: float
    potential_monthly_savings: float
    discretionary_spending: float
    recommendations: List[str]
    timestamp: str

class RecurringExpenses(BaseModel):
    recurring_expenses: List[Dict]
    total_monthly_recurring: float
    timestamp: str

class BudgetAnalysis(BaseModel):
    categories: Dict
    alerts: List[str]
    timestamp: str

# Routes
@router.post("/categorize", response_model=CategoryPrediction)
async def predict_category(
    description: str,
    current_user: User = Depends(get_current_user)
):
    """Predict category for a transaction description."""
    category = categorizer.categorize(description)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to categorize transaction"
        )
    
    confidence = categorizer.get_confidence_score(description, category)
    return CategoryPrediction(category=category, confidence=confidence)

@router.get("/spending-analysis", response_model=SpendingAnalysis)
async def analyze_spending(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate spending analysis for the current user."""
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).all()
    
    analysis = insights.analyze_spending_patterns([t.__dict__ for t in transactions])
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating spending analysis"
        )
    
    return analysis

@router.get("/forecast", response_model=ForecastResponse)
async def get_expense_forecast(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Predict future expenses."""
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).all()
    
    forecast = insights.predict_future_expenses(
        [t.__dict__ for t in transactions],
        days_ahead=days
    )
    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating forecast"
        )
    
    return forecast

@router.get("/savings-recommendations", response_model=SavingsRecommendation)
async def get_savings_recommendations(
    monthly_income: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate personalized savings recommendations."""
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).all()
    
    recommendations = insights.generate_savings_recommendations(
        [t.__dict__ for t in transactions],
        income=monthly_income
    )
    if not recommendations:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating savings recommendations"
        )
    
    return recommendations

@router.get("/recurring-expenses", response_model=RecurringExpenses)
async def detect_recurring_expenses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Detect recurring expenses and subscriptions."""
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).all()
    
    recurring = insights.detect_recurring_expenses([t.__dict__ for t in transactions])
    if not recurring:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error detecting recurring expenses"
        )
    
    return recurring

@router.get("/budget-analysis", response_model=BudgetAnalysis)
async def analyze_budget(
    budget_limits: Dict[str, float],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze spending against budget limits."""
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).all()
    
    analysis = insights.get_budget_analysis(
        [t.__dict__ for t in transactions],
        budget_limits
    )
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error analyzing budget"
        )
    
    return analysis
