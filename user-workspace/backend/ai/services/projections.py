from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.linear_model import LinearRegression
from collections import defaultdict

class FinancialProjectionService:
    """Service for generating financial projections and cash flow analysis."""

    def generate_cash_flow_projection(
        self,
        transactions: List[Dict],
        assets: List[Dict],
        debts: List[Dict],
        months_ahead: int = 12
    ) -> Dict:
        """
        Generate comprehensive cash flow projections.
        
        Args:
            transactions: Historical transactions
            assets: Current assets
            debts: Current debts
            months_ahead: Number of months to project
            
        Returns:
            Dict containing cash flow projections and analysis
        """
        df = pd.DataFrame(transactions)
        
        # Prepare data for Prophet
        prophet_df = pd.DataFrame({
            'ds': df['transaction_date'],
            'y': df['amount']
        })
        
        # Initialize Prophet model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False
        )
        
        # Fit model and make predictions
        model.fit(prophet_df)
        future = model.make_future_dataframe(periods=months_ahead * 30)
        forecast = model.predict(future)
        
        # Calculate projected cash flows
        income_projection = self._project_income(df, months_ahead)
        expense_projection = self._project_expenses(df, months_ahead)
        debt_payments = self._calculate_debt_payments(debts, months_ahead)
        asset_returns = self._project_asset_returns(assets, months_ahead)
        
        # Combine all projections
        monthly_projections = {}
        for month in range(1, months_ahead + 1):
            date = datetime.now() + timedelta(days=30 * month)
            monthly_projections[month] = {
                "date": date.isoformat(),
                "projected_income": income_projection[month],
                "projected_expenses": expense_projection[month],
                "debt_payments": debt_payments[month],
                "asset_returns": asset_returns[month],
                "net_cash_flow": (
                    income_projection[month] +
                    asset_returns[month] -
                    expense_projection[month] -
                    debt_payments[month]
                )
            }
        
        return {
            "monthly_projections": monthly_projections,
            "summary": self._generate_projection_summary(monthly_projections),
            "risk_analysis": self._analyze_projection_risks(monthly_projections),
            "recommendations": self._generate_recommendations(monthly_projections),
            "generated_at": datetime.now().isoformat()
        }

    def generate_net_worth_projection(
        self,
        assets: List[Dict],
        debts: List[Dict],
        months_ahead: int = 12
    ) -> Dict:
        """Generate net worth projections."""
        current_net_worth = sum(asset['value'] for asset in assets) - \
                          sum(debt['current_balance'] for debt in debts)
        
        # Project asset growth
        asset_projections = self._project_asset_growth(assets, months_ahead)
        
        # Project debt reduction
        debt_projections = self._project_debt_reduction(debts, months_ahead)
        
        # Calculate monthly net worth projections
        monthly_projections = {}
        for month in range(1, months_ahead + 1):
            date = datetime.now() + timedelta(days=30 * month)
            monthly_projections[month] = {
                "date": date.isoformat(),
                "projected_assets": asset_projections[month],
                "projected_debts": debt_projections[month],
                "net_worth": asset_projections[month] - debt_projections[month]
            }
        
        return {
            "current_net_worth": current_net_worth,
            "monthly_projections": monthly_projections,
            "analysis": self._analyze_net_worth_trends(monthly_projections),
            "generated_at": datetime.now().isoformat()
        }

    def generate_savings_projection(
        self,
        transactions: List[Dict],
        monthly_income: float,
        savings_goal: float,
        months_ahead: int = 12
    ) -> Dict:
        """Generate savings projections and goal tracking."""
        df = pd.DataFrame(transactions)
        
        # Calculate current savings rate
        income = df[df['type'] == 'income']['amount'].sum()
        expenses = df[df['type'] == 'expense']['amount'].sum()
        current_savings_rate = ((income - expenses) / income * 100) if income > 0 else 0
        
        # Project future savings
        monthly_savings = monthly_income * (current_savings_rate / 100)
        projected_savings = {}
        
        accumulated_savings = 0
        for month in range(1, months_ahead + 1):
            date = datetime.now() + timedelta(days=30 * month)
            accumulated_savings += monthly_savings
            
            projected_savings[month] = {
                "date": date.isoformat(),
                "monthly_savings": monthly_savings,
                "accumulated_savings": accumulated_savings,
                "goal_progress": (accumulated_savings / savings_goal * 100) if savings_goal > 0 else 0
            }
        
        return {
            "current_savings_rate": current_savings_rate,
            "monthly_savings_target": monthly_savings,
            "savings_goal": savings_goal,
            "monthly_projections": projected_savings,
            "goal_analysis": self._analyze_savings_goal(projected_savings, savings_goal),
            "generated_at": datetime.now().isoformat()
        }

    def _project_income(self, df: pd.DataFrame, months_ahead: int) -> Dict[int, float]:
        """Project future income based on historical data."""
        income_df = df[df['type'] == 'income']
        
        if income_df.empty:
            return {month: 0 for month in range(1, months_ahead + 1)}
        
        # Calculate monthly income trends
        monthly_income = income_df.groupby(
            pd.Grouper(key='transaction_date', freq='M')
        )['amount'].sum()
        
        # Use linear regression for projection
        X = np.array(range(len(monthly_income))).reshape(-1, 1)
        y = monthly_income.values
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Project future months
        future_months = np.array(range(len(monthly_income), len(monthly_income) + months_ahead)).reshape(-1, 1)
        projected_income = model.predict(future_months)
        
        return {month: max(0, float(income)) for month, income in enumerate(projected_income, 1)}

    def _project_expenses(self, df: pd.DataFrame, months_ahead: int) -> Dict[int, float]:
        """Project future expenses based on historical data."""
        expense_df = df[df['type'] == 'expense']
        
        if expense_df.empty:
            return {month: 0 for month in range(1, months_ahead + 1)}
        
        # Calculate monthly expense trends
        monthly_expenses = expense_df.groupby(
            pd.Grouper(key='transaction_date', freq='M')
        )['amount'].sum()
        
        # Use linear regression for projection
        X = np.array(range(len(monthly_expenses))).reshape(-1, 1)
        y = monthly_expenses.values
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Project future months
        future_months = np.array(range(len(monthly_expenses), len(monthly_expenses) + months_ahead)).reshape(-1, 1)
        projected_expenses = model.predict(future_months)
        
        return {month: max(0, float(expense)) for month, expense in enumerate(projected_expenses, 1)}

    def _calculate_debt_payments(self, debts: List[Dict], months_ahead: int) -> Dict[int, float]:
        """Calculate future debt payments."""
        monthly_payments = defaultdict(float)
        
        for debt in debts:
            if debt['status'] != 'paid_off':
                payment_amount = debt.get('payment_amount', 0)
                for month in range(1, months_ahead + 1):
                    monthly_payments[month] += payment_amount
        
        return dict(monthly_payments)

    def _project_asset_returns(self, assets: List[Dict], months_ahead: int) -> Dict[int, float]:
        """Project future returns from assets."""
        monthly_returns = defaultdict(float)
        
        for asset in assets:
            annual_return = asset.get('annual_return', 0)
            monthly_return = (annual_return / 12 / 100) * asset['value']
            
            for month in range(1, months_ahead + 1):
                monthly_returns[month] += monthly_return
        
        return dict(monthly_returns)

    def _project_asset_growth(self, assets: List[Dict], months_ahead: int) -> Dict[int, float]:
        """Project asset value growth."""
        monthly_values = defaultdict(float)
        
        for asset in assets:
            current_value = asset['value']
            annual_return = asset.get('annual_return', 0)
            monthly_growth_rate = annual_return / 12 / 100
            
            for month in range(1, months_ahead + 1):
                current_value *= (1 + monthly_growth_rate)
                monthly_values[month] += current_value
        
        return dict(monthly_values)

    def _project_debt_reduction(self, debts: List[Dict], months_ahead: int) -> Dict[int, float]:
        """Project debt reduction over time."""
        monthly_balances = defaultdict(float)
        
        for debt in debts:
            current_balance = debt['current_balance']
            payment_amount = debt.get('payment_amount', 0)
            interest_rate = debt.get('interest_rate', 0)
            monthly_interest_rate = interest_rate / 12 / 100
            
            for month in range(1, months_ahead + 1):
                interest = current_balance * monthly_interest_rate
                current_balance = max(0, current_balance + interest - payment_amount)
                monthly_balances[month] += current_balance
        
        return dict(monthly_balances)

    def _generate_projection_summary(self, projections: Dict) -> Dict:
        """Generate summary of projections."""
        total_income = sum(month['projected_income'] for month in projections.values())
        total_expenses = sum(month['projected_expenses'] for month in projections.values())
        total_debt_payments = sum(month['debt_payments'] for month in projections.values())
        total_asset_returns = sum(month['asset_returns'] for month in projections.values())
        
        return {
            "total_projected_income": total_income,
            "total_projected_expenses": total_expenses,
            "total_debt_payments": total_debt_payments,
            "total_asset_returns": total_asset_returns,
            "net_position": total_income + total_asset_returns - total_expenses - total_debt_payments,
            "average_monthly_cash_flow": (total_income + total_asset_returns - total_expenses - total_debt_payments) / len(projections)
        }

    def _analyze_projection_risks(self, projections: Dict) -> Dict:
        """Analyze risks in the projections."""
        monthly_cash_flows = [p['net_cash_flow'] for p in projections.values()]
        
        return {
            "negative_months": sum(1 for cf in monthly_cash_flows if cf < 0),
            "lowest_cash_flow": min(monthly_cash_flows),
            "cash_flow_volatility": np.std(monthly_cash_flows),
            "risk_level": "high" if np.std(monthly_cash_flows) > np.mean(monthly_cash_flows) else "medium" if np.std(monthly_cash_flows) > np.mean(monthly_cash_flows)/2 else "low"
        }

    def _generate_recommendations(self, projections: Dict) -> List[str]:
        """Generate recommendations based on projections."""
        recommendations = []
        summary = self._generate_projection_summary(projections)
        risks = self._analyze_projection_risks(projections)
        
        if summary['net_position'] < 0:
            recommendations.append("Consider reducing expenses or increasing income to improve cash flow")
        
        if risks['negative_months'] > 0:
            recommendations.append(f"Build emergency fund to cover {risks['negative_months']} months of potential negative cash flow")
        
        if risks['risk_level'] == "high":
            recommendations.append("Consider diversifying income sources to reduce cash flow volatility")
        
        return recommendations

    def _analyze_net_worth_trends(self, projections: Dict) -> Dict:
        """Analyze trends in net worth projections."""
        net_worth_values = [p['net_worth'] for p in projections.values()]
        
        return {
            "trend": "increasing" if net_worth_values[-1] > net_worth_values[0] else "decreasing",
            "growth_rate": ((net_worth_values[-1] / net_worth_values[0]) - 1) * 100 if net_worth_values[0] != 0 else 0,
            "volatility": np.std(net_worth_values),
            "projected_final": net_worth_values[-1]
        }

    def _analyze_savings_goal(self, projections: Dict, goal: float) -> Dict:
        """Analyze progress towards savings goal."""
        final_savings = list(projections.values())[-1]['accumulated_savings']
        
        return {
            "will_reach_goal": final_savings >= goal,
            "months_to_goal": next((k for k, v in projections.items() if v['accumulated_savings'] >= goal), None),
            "final_amount": final_savings,
            "goal_completion_percentage": (final_savings / goal * 100) if goal > 0 else 0
        }
