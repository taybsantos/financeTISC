from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta
import pandas as pd
from prophet import Prophet
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)

class FinancialInsights:
    """Service for generating AI-powered financial insights and predictions."""

    def __init__(self):
        """Initialize the financial insights service."""
        self.prophet_model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False
        )

    def analyze_spending_patterns(self, transactions: List[Dict]) -> Dict:
        """
        Analyze spending patterns and generate insights.
        
        Args:
            transactions (List[Dict]): List of transaction records
            
        Returns:
            Dict: Analysis results and insights
        """
        try:
            # Convert transactions to DataFrame
            df = pd.DataFrame(transactions)
            
            # Basic statistics
            total_spending = df[df['type'] == 'expense']['amount'].sum()
            avg_daily_spending = total_spending / (df['transaction_date'].max() - 
                                                 df['transaction_date'].min()).days
            
            # Category analysis
            category_spending = df[df['type'] == 'expense'].groupby('category')['amount'].agg([
                'sum', 'count', 'mean'
            ]).to_dict('index')
            
            # Find unusual transactions
            amount_std = df[df['type'] == 'expense']['amount'].std()
            amount_mean = df[df['type'] == 'expense']['amount'].mean()
            unusual_transactions = df[
                (df['type'] == 'expense') & 
                (df['amount'] > amount_mean + 2 * amount_std)
            ].to_dict('records')
            
            return {
                'total_spending': float(total_spending),
                'average_daily_spending': float(avg_daily_spending),
                'category_analysis': category_spending,
                'unusual_transactions': unusual_transactions,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing spending patterns: {str(e)}")
            return {}

    def predict_future_expenses(self, 
                              transactions: List[Dict], 
                              days_ahead: int = 30) -> Dict:
        """
        Predict future expenses using Prophet.
        
        Args:
            transactions (List[Dict]): Historical transactions
            days_ahead (int): Number of days to forecast
            
        Returns:
            Dict: Forecast results
        """
        try:
            # Prepare data for Prophet
            df = pd.DataFrame(transactions)
            prophet_df = pd.DataFrame({
                'ds': df['transaction_date'],
                'y': df[df['type'] == 'expense']['amount']
            })
            
            # Fit model
            self.prophet_model.fit(prophet_df)
            
            # Make forecast
            future_dates = self.prophet_model.make_future_dataframe(periods=days_ahead)
            forecast = self.prophet_model.predict(future_dates)
            
            return {
                'forecast': forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
                .tail(days_ahead)
                .to_dict('records'),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error predicting future expenses: {str(e)}")
            return {}

    def generate_savings_recommendations(self, 
                                      transactions: List[Dict],
                                      income: float) -> Dict:
        """
        Generate personalized savings recommendations.
        
        Args:
            transactions (List[Dict]): Transaction history
            income (float): Monthly income
            
        Returns:
            Dict: Savings recommendations
        """
        try:
            df = pd.DataFrame(transactions)
            monthly_expenses = df[df['type'] == 'expense'].groupby(
                pd.Grouper(key='transaction_date', freq='M')
            )['amount'].sum()
            
            avg_monthly_expenses = monthly_expenses.mean()
            
            # Calculate potential savings
            potential_savings = income - avg_monthly_expenses
            savings_rate = (potential_savings / income) * 100
            
            # Analyze discretionary spending
            discretionary_categories = ['entertainment', 'shopping', 'dining']
            discretionary_spending = df[
                (df['type'] == 'expense') & 
                (df['category'].isin(discretionary_categories))
            ]['amount'].sum()
            
            recommendations = []
            
            if savings_rate < 20:
                recommendations.append(
                    "Consider reducing discretionary spending to achieve a 20% savings rate"
                )
            
            if discretionary_spending > 0.3 * income:
                recommendations.append(
                    "Your discretionary spending is high. Consider setting a budget for non-essential expenses"
                )
            
            return {
                'current_savings_rate': float(savings_rate),
                'potential_monthly_savings': float(potential_savings),
                'discretionary_spending': float(discretionary_spending),
                'recommendations': recommendations,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating savings recommendations: {str(e)}")
            return {}

    def detect_recurring_expenses(self, transactions: List[Dict]) -> Dict:
        """
        Detect recurring expenses and subscriptions.
        
        Args:
            transactions (List[Dict]): Transaction history
            
        Returns:
            Dict: Detected recurring expenses
        """
        try:
            df = pd.DataFrame(transactions)
            df['transaction_date'] = pd.to_datetime(df['transaction_date'])
            
            # Group similar transactions
            similar_transactions = defaultdict(list)
            
            for _, row in df.iterrows():
                if row['type'] != 'expense':
                    continue
                    
                amount = row['amount']
                description = row['description'].lower()
                
                key = f"{description}_{amount}"
                similar_transactions[key].append(row['transaction_date'])
            
            recurring_expenses = []
            
            for key, dates in similar_transactions.items():
                if len(dates) >= 2:  # At least 2 occurrences
                    dates.sort()
                    
                    # Calculate average interval
                    intervals = [(dates[i+1] - dates[i]).days 
                               for i in range(len(dates)-1)]
                    avg_interval = sum(intervals) / len(intervals)
                    
                    # Check if relatively consistent
                    if 25 <= avg_interval <= 35:  # Monthly
                        period = "monthly"
                    elif 6 <= avg_interval <= 8:  # Weekly
                        period = "weekly"
                    else:
                        continue
                    
                    description, amount = key.rsplit('_', 1)
                    recurring_expenses.append({
                        'description': description,
                        'amount': float(amount),
                        'period': period,
                        'last_charge': max(dates).isoformat(),
                        'next_expected': (max(dates) + 
                                        timedelta(days=avg_interval)).isoformat()
                    })
            
            return {
                'recurring_expenses': recurring_expenses,
                'total_monthly_recurring': sum(
                    float(exp['amount']) 
                    for exp in recurring_expenses 
                    if exp['period'] == 'monthly'
                ),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error detecting recurring expenses: {str(e)}")
            return {}

    def get_budget_analysis(self, 
                          transactions: List[Dict], 
                          budget_limits: Dict[str, float]) -> Dict:
        """
        Analyze spending against budget limits.
        
        Args:
            transactions (List[Dict]): Transaction history
            budget_limits (Dict[str, float]): Category-wise budget limits
            
        Returns:
            Dict: Budget analysis and alerts
        """
        try:
            df = pd.DataFrame(transactions)
            current_month = datetime.now().replace(day=1)
            
            # Filter current month's expenses
            current_expenses = df[
                (df['type'] == 'expense') &
                (df['transaction_date'] >= current_month)
            ]
            
            category_spending = current_expenses.groupby('category')['amount'].sum()
            
            analysis = {
                'categories': {},
                'alerts': [],
                'timestamp': datetime.now().isoformat()
            }
            
            for category, limit in budget_limits.items():
                spent = float(category_spending.get(category, 0))
                remaining = limit - spent
                percentage_used = (spent / limit * 100) if limit > 0 else 0
                
                analysis['categories'][category] = {
                    'limit': limit,
                    'spent': spent,
                    'remaining': remaining,
                    'percentage_used': percentage_used
                }
                
                # Generate alerts
                if percentage_used >= 90:
                    analysis['alerts'].append(
                        f"Warning: {category} spending at {percentage_used:.1f}% of budget"
                    )
                elif percentage_used >= 75:
                    analysis['alerts'].append(
                        f"Notice: {category} spending at {percentage_used:.1f}% of budget"
                    )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing budget: {str(e)}")
            return {}
