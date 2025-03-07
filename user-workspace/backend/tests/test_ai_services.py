import pytest
from datetime import datetime, timedelta
from backend.ai.services.categorization import TransactionCategorizer
from backend.ai.services.insights import FinancialInsights

@pytest.fixture
def categorizer():
    return TransactionCategorizer()

@pytest.fixture
def insights():
    return FinancialInsights()

@pytest.fixture
def sample_transactions():
    return [
        {
            "id": "1",
            "amount": 50.0,
            "description": "Netflix subscription",
            "type": "expense",
            "category": "entertainment",
            "transaction_date": datetime.now() - timedelta(days=30),
            "status": "completed"
        },
        {
            "id": "2",
            "amount": 100.0,
            "description": "Grocery shopping at Walmart",
            "type": "expense",
            "category": "food",
            "transaction_date": datetime.now() - timedelta(days=15),
            "status": "completed"
        },
        {
            "id": "3",
            "amount": 3000.0,
            "description": "Monthly salary",
            "type": "income",
            "category": "salary",
            "transaction_date": datetime.now() - timedelta(days=1),
            "status": "completed"
        }
    ]

def test_transaction_categorization(categorizer):
    """Test transaction categorization functionality."""
    # Test entertainment category
    netflix_category = categorizer.categorize("Netflix monthly subscription")
    assert netflix_category == "entertainment"
    
    # Test food category
    grocery_category = categorizer.categorize("Walmart Grocery Shopping")
    assert grocery_category == "food"
    
    # Test confidence scores
    netflix_confidence = categorizer.get_confidence_score(
        "Netflix monthly subscription",
        "entertainment"
    )
    assert 0 <= netflix_confidence <= 1

def test_spending_analysis(insights, sample_transactions):
    """Test spending pattern analysis."""
    analysis = insights.analyze_spending_patterns(sample_transactions)
    
    assert isinstance(analysis, dict)
    assert "total_spending" in analysis
    assert "average_daily_spending" in analysis
    assert "category_analysis" in analysis
    assert analysis["total_spending"] == 150.0  # Sum of expenses

def test_savings_recommendations(insights, sample_transactions):
    """Test savings recommendations generation."""
    recommendations = insights.generate_savings_recommendations(
        sample_transactions,
        income=3000.0
    )
    
    assert isinstance(recommendations, dict)
    assert "current_savings_rate" in recommendations
    assert "potential_monthly_savings" in recommendations
    assert "recommendations" in recommendations
    assert isinstance(recommendations["recommendations"], list)

def test_recurring_expenses(insights, sample_transactions):
    """Test recurring expenses detection."""
    recurring = insights.detect_recurring_expenses(sample_transactions)
    
    assert isinstance(recurring, dict)
    assert "recurring_expenses" in recurring
    assert "total_monthly_recurring" in recurring
    assert isinstance(recurring["recurring_expenses"], list)

def test_budget_analysis(insights, sample_transactions):
    """Test budget analysis."""
    budget_limits = {
        "entertainment": 100.0,
        "food": 300.0
    }
    
    analysis = insights.get_budget_analysis(sample_transactions, budget_limits)
    
    assert isinstance(analysis, dict)
    assert "categories" in analysis
    assert "alerts" in analysis
    assert isinstance(analysis["alerts"], list)
    assert "entertainment" in analysis["categories"]
    assert "food" in analysis["categories"]

def test_future_expenses_prediction(insights, sample_transactions):
    """Test expense prediction functionality."""
    forecast = insights.predict_future_expenses(sample_transactions, days_ahead=30)
    
    assert isinstance(forecast, dict)
    assert "forecast" in forecast
    assert isinstance(forecast["forecast"], list)
    assert len(forecast["forecast"]) <= 30  # Should not exceed requested days
