from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from collections import defaultdict

class FinancialReportService:
    """Service for generating comprehensive financial reports and analytics."""

    def generate_monthly_report(self, transactions: List[Dict], month: int, year: int) -> Dict:
        """
        Generate a comprehensive monthly financial report.
        
        Args:
            transactions: List of transactions
            month: Target month (1-12)
            year: Target year
            
        Returns:
            Dict containing monthly financial analysis
        """
        df = pd.DataFrame(transactions)
        
        # Filter for the specified month
        mask = (df['transaction_date'].dt.month == month) & \
               (df['transaction_date'].dt.year == year)
        monthly_df = df[mask]
        
        # Calculate income and expenses
        income = monthly_df[monthly_df['type'] == 'income']['amount'].sum()
        expenses = monthly_df[monthly_df['type'] == 'expense']['amount'].sum()
        balance = income - expenses
        
        # Category breakdown
        category_expenses = monthly_df[monthly_df['type'] == 'expense'].groupby('category')['amount'].agg([
            'sum',
            'count',
            'mean'
        ]).to_dict('index')
        
        # Daily spending pattern
        daily_expenses = monthly_df[monthly_df['type'] == 'expense'].groupby(
            monthly_df['transaction_date'].dt.day
        )['amount'].sum().to_dict()
        
        # Recurring expenses
        recurring = self._identify_recurring_expenses(monthly_df)
        
        # Budget analysis
        budget_status = self._analyze_budget_status(monthly_df)
        
        # Savings rate
        savings_rate = ((income - expenses) / income * 100) if income > 0 else 0
        
        return {
            "summary": {
                "total_income": float(income),
                "total_expenses": float(expenses),
                "net_balance": float(balance),
                "savings_rate": float(savings_rate)
            },
            "category_analysis": category_expenses,
            "daily_spending": daily_expenses,
            "recurring_expenses": recurring,
            "budget_status": budget_status,
            "month": month,
            "year": year,
            "generated_at": datetime.now().isoformat()
        }

    def generate_annual_report(self, transactions: List[Dict], year: int) -> Dict:
        """Generate annual financial report."""
        df = pd.DataFrame(transactions)
        annual_df = df[df['transaction_date'].dt.year == year]
        
        # Monthly trends
        monthly_trends = self._calculate_monthly_trends(annual_df)
        
        # Year-over-year comparison
        yoy_comparison = self._calculate_yoy_comparison(df, year)
        
        # Category trends
        category_trends = self._analyze_category_trends(annual_df)
        
        # Annual goals progress
        goals_progress = self._analyze_goals_progress(annual_df)
        
        return {
            "monthly_trends": monthly_trends,
            "year_over_year": yoy_comparison,
            "category_trends": category_trends,
            "goals_progress": goals_progress,
            "year": year,
            "generated_at": datetime.now().isoformat()
        }

    def generate_tax_report(self, transactions: List[Dict], year: int) -> Dict:
        """Generate tax-related financial report."""
        df = pd.DataFrame(transactions)
        tax_year_df = df[df['transaction_date'].dt.year == year]
        
        # Income categorization
        income_sources = self._categorize_income_sources(tax_year_df)
        
        # Deductible expenses
        deductible_expenses = self._identify_deductible_expenses(tax_year_df)
        
        # Tax categories summary
        tax_categories = self._summarize_tax_categories(tax_year_df)
        
        return {
            "income_sources": income_sources,
            "deductible_expenses": deductible_expenses,
            "tax_categories": tax_categories,
            "year": year,
            "generated_at": datetime.now().isoformat()
        }

    def _identify_recurring_expenses(self, df: pd.DataFrame) -> List[Dict]:
        """Identify recurring expenses from transactions."""
        recurring = []
        
        if df.empty:
            return recurring
            
        for _, group in df.groupby(['description', 'amount']):
            if len(group) >= 2:  # At least 2 occurrences
                dates = sorted(group['transaction_date'])
                intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
                
                if intervals:
                    avg_interval = sum(intervals) / len(intervals)
                    if 25 <= avg_interval <= 35:  # Monthly
                        period = "monthly"
                    elif 6 <= avg_interval <= 8:  # Weekly
                        period = "weekly"
                    else:
                        continue
                        
                    recurring.append({
                        "description": group['description'].iloc[0],
                        "amount": float(group['amount'].iloc[0]),
                        "period": period,
                        "category": group['category'].iloc[0],
                        "last_date": dates[-1].isoformat()
                    })
                    
        return recurring

    def _analyze_budget_status(self, df: pd.DataFrame) -> Dict:
        """Analyze budget status for each category."""
        if df.empty:
            return {}
            
        category_expenses = df[df['type'] == 'expense'].groupby('category')['amount'].sum()
        
        # Example budget limits (should be customizable per user)
        budget_limits = {
            "Housing": 2000,
            "Transportation": 500,
            "Food": 600,
            "Entertainment": 200
        }
        
        status = {}
        for category, spent in category_expenses.items():
            limit = budget_limits.get(category, 0)
            if limit > 0:
                status[category] = {
                    "spent": float(spent),
                    "limit": limit,
                    "remaining": limit - float(spent),
                    "percentage_used": (float(spent) / limit * 100)
                }
                
        return status

    def _calculate_monthly_trends(self, df: pd.DataFrame) -> Dict:
        """Calculate monthly financial trends."""
        monthly_data = {}
        
        for month in range(1, 13):
            month_df = df[df['transaction_date'].dt.month == month]
            if not month_df.empty:
                income = month_df[month_df['type'] == 'income']['amount'].sum()
                expenses = month_df[month_df['type'] == 'expense']['amount'].sum()
                
                monthly_data[month] = {
                    "income": float(income),
                    "expenses": float(expenses),
                    "balance": float(income - expenses)
                }
                
        return monthly_data

    def _calculate_yoy_comparison(self, df: pd.DataFrame, year: int) -> Dict:
        """Calculate year-over-year comparison."""
        current_year = df[df['transaction_date'].dt.year == year]
        previous_year = df[df['transaction_date'].dt.year == year - 1]
        
        def calculate_yearly_metrics(year_df):
            if year_df.empty:
                return {
                    "total_income": 0,
                    "total_expenses": 0,
                    "savings_rate": 0
                }
            
            income = year_df[year_df['type'] == 'income']['amount'].sum()
            expenses = year_df[year_df['type'] == 'expense']['amount'].sum()
            savings_rate = ((income - expenses) / income * 100) if income > 0 else 0
            
            return {
                "total_income": float(income),
                "total_expenses": float(expenses),
                "savings_rate": float(savings_rate)
            }
        
        return {
            "current_year": calculate_yearly_metrics(current_year),
            "previous_year": calculate_yearly_metrics(previous_year)
        }

    def _analyze_category_trends(self, df: pd.DataFrame) -> Dict:
        """Analyze spending trends by category."""
        if df.empty:
            return {}
            
        category_trends = {}
        
        for category in df['category'].unique():
            cat_df = df[df['category'] == category]
            monthly_amounts = cat_df.groupby(cat_df['transaction_date'].dt.month)['amount'].sum()
            
            if not monthly_amounts.empty:
                trend = np.polyfit(monthly_amounts.index, monthly_amounts.values, 1)[0]
                
                category_trends[category] = {
                    "total_spent": float(cat_df['amount'].sum()),
                    "average_monthly": float(cat_df['amount'].mean()),
                    "trend": "increasing" if trend > 0 else "decreasing",
                    "trend_value": float(trend)
                }
                
        return category_trends

    def _analyze_goals_progress(self, df: pd.DataFrame) -> Dict:
        """Analyze progress towards financial goals."""
        # Example goals (should be customizable per user)
        goals = {
            "savings": 10000,
            "expense_reduction": 0.1,  # 10% reduction
            "emergency_fund": 5000
        }
        
        if df.empty:
            return {"goals": goals, "progress": {}}
            
        income = df[df['type'] == 'income']['amount'].sum()
        expenses = df[df['type'] == 'expense']['amount'].sum()
        savings = income - expenses
        
        progress = {
            "savings": {
                "target": goals["savings"],
                "current": float(savings),
                "percentage": float((savings / goals["savings"]) * 100) if goals["savings"] > 0 else 0
            },
            "expense_reduction": {
                "target": goals["expense_reduction"],
                "current": 0,  # Need historical data to calculate
                "percentage": 0  # Need historical data to calculate
            },
            "emergency_fund": {
                "target": goals["emergency_fund"],
                "current": float(savings),  # Assuming savings go to emergency fund
                "percentage": float((savings / goals["emergency_fund"]) * 100) if goals["emergency_fund"] > 0 else 0
            }
        }
        
        return {
            "goals": goals,
            "progress": progress
        }

    def _categorize_income_sources(self, df: pd.DataFrame) -> Dict:
        """Categorize and summarize income sources."""
        if df.empty:
            return {}
            
        income_df = df[df['type'] == 'income']
        sources = income_df.groupby('category')['amount'].agg([
            'sum',
            'count',
            'mean'
        ]).to_dict('index')
        
        return {
            category: {
                "total": float(values['sum']),
                "count": int(values['count']),
                "average": float(values['mean'])
            }
            for category, values in sources.items()
        }

    def _identify_deductible_expenses(self, df: pd.DataFrame) -> Dict:
        """Identify potentially tax-deductible expenses."""
        if df.empty:
            return {}
            
        # Categories typically tax-deductible (should be customizable)
        deductible_categories = [
            "Healthcare",
            "Education",
            "Business",
            "Charitable Donations",
            "Mortgage Interest"
        ]
        
        deductible_df = df[
            (df['type'] == 'expense') & 
            (df['category'].isin(deductible_categories))
        ]
        
        deductions = deductible_df.groupby('category')['amount'].agg([
            'sum',
            'count'
        ]).to_dict('index')
        
        return {
            category: {
                "total": float(values['sum']),
                "count": int(values['count'])
            }
            for category, values in deductions.items()
        }

    def _summarize_tax_categories(self, df: pd.DataFrame) -> Dict:
        """Summarize transactions by tax category."""
        if df.empty:
            return {}
            
        # Define tax categories
        tax_categories = {
            "income": ["Salary", "Freelance", "Investments"],
            "deductions": ["Healthcare", "Education", "Charitable Donations"],
            "expenses": ["Business", "Office Supplies", "Professional Development"]
        }
        
        summary = {}
        for tax_type, categories in tax_categories.items():
            filtered_df = df[df['category'].isin(categories)]
            if not filtered_df.empty:
                summary[tax_type] = {
                    "total": float(filtered_df['amount'].sum()),
                    "categories": {
                        cat: float(filtered_df[filtered_df['category'] == cat]['amount'].sum())
                        for cat in categories
                        if not filtered_df[filtered_df['category'] == cat].empty
                    }
                }
                
        return summary
