from datetime import datetime, timedelta
from typing import List, Dict
import numpy as np
from prophet import Prophet
from sklearn.linear_model import LinearRegression

from backend.models.asset import Asset, AssetType
from backend.models.debt import Debt, PaymentFrequency

def calculate_monthly_payment(debt: Debt) -> float:
    """Calculate standardized monthly payment for a debt."""
    if not debt.payment_amount:
        return 0
        
    if debt.payment_frequency == PaymentFrequency.WEEKLY:
        return debt.payment_amount * 52/12
    elif debt.payment_frequency == PaymentFrequency.BI_WEEKLY:
        return debt.payment_amount * 26/12
    elif debt.payment_frequency == PaymentFrequency.QUARTERLY:
        return debt.payment_amount / 3
    elif debt.payment_frequency == PaymentFrequency.ANNUALLY:
        return debt.payment_amount / 12
    else:  # MONTHLY
        return debt.payment_amount

def project_asset_value(asset: Asset, months: int) -> List[float]:
    """Project asset value over time using appropriate method based on asset type."""
    if not asset.current_value:
        return [asset.value] * (months + 1)

    historical_values = []  # In a real app, we'd fetch historical values from the database
    
    if asset.type in [AssetType.STOCK, AssetType.ETF, AssetType.MUTUAL_FUND]:
        # Use Prophet for market-based assets
        df = pd.DataFrame({
            'ds': [datetime.now() - timedelta(days=i*30) for i in range(12, 0, -1)],
            'y': historical_values if historical_values else [asset.current_value] * 12
        })
        
        model = Prophet(yearly_seasonality=True)
        model.fit(df)
        
        future = model.make_future_dataframe(periods=months, freq='M')
        forecast = model.predict(future)
        return [asset.current_value] + forecast['yhat'].tolist()[-months:]
        
    elif asset.type in [AssetType.REAL_ESTATE]:
        # Use linear regression for real estate
        X = np.array(range(12)).reshape(-1, 1)
        y = historical_values if historical_values else [asset.current_value] * 12
        
        model = LinearRegression()
        model.fit(X, y)
        
        future_X = np.array(range(12, 12 + months)).reshape(-1, 1)
        predictions = model.predict(future_X)
        return [asset.current_value] + predictions.tolist()
        
    elif asset.type in [AssetType.BANK_ACCOUNT, AssetType.CASH]:
        # Simple interest calculation for cash-like assets
        if asset.interest_rate:
            monthly_rate = asset.interest_rate / 12 / 100
            values = []
            current = asset.current_value
            for _ in range(months + 1):
                values.append(current)
                current *= (1 + monthly_rate)
            return values
        else:
            return [asset.current_value] * (months + 1)
            
    else:
        # Default to flat projection
        return [asset.current_value] * (months + 1)

def project_debt_balance(debt: Debt, months: int) -> List[float]:
    """Project debt balance over time considering payments and interest."""
    if not debt.current_balance or not debt.interest_rate:
        return [debt.current_balance] * (months + 1)
        
    monthly_rate = debt.interest_rate / 12 / 100
    monthly_payment = calculate_monthly_payment(debt)
    
    balances = []
    current_balance = debt.current_balance
    
    for _ in range(months + 1):
        balances.append(current_balance)
        if current_balance <= 0:
            continue
            
        # Add interest
        interest = current_balance * monthly_rate
        current_balance += interest
        
        # Subtract payment
        current_balance = max(0, current_balance - monthly_payment)
    
    return balances

def calculate_portfolio_projections(
    assets: List[Asset],
    debts: List[Debt],
    months: int
) -> Dict:
    """Calculate portfolio projections including assets, debts, and net worth."""
    # Initialize projection arrays
    asset_projections = {asset.id: project_asset_value(asset, months) for asset in assets}
    debt_projections = {debt.id: project_debt_balance(debt, months) for debt in debts}
    
    # Calculate monthly totals
    monthly_projections = []
    for month in range(months + 1):
        total_assets = sum(proj[month] for proj in asset_projections.values())
        total_debts = sum(proj[month] for proj in debt_projections.values())
        net_worth = total_assets - total_debts
        
        monthly_projections.append({
            "month": month,
            "date": (datetime.now() + timedelta(days=30*month)).strftime("%Y-%m-%d"),
            "total_assets": round(total_assets, 2),
            "total_debts": round(total_debts, 2),
            "net_worth": round(net_worth, 2)
        })
    
    return {
        "current_net_worth": monthly_projections[0]["net_worth"],
        "monthly_projections": monthly_projections[1:],  # Exclude current month
        "asset_projections": asset_projections,
        "debt_projections": debt_projections
    }
