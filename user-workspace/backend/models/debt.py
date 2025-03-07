from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, Text, Integer
from sqlalchemy.sql import func
import enum
from datetime import datetime

from backend.config.database import Base

class DebtType(str, enum.Enum):
    CREDIT_CARD = "credit_card"
    STUDENT_LOAN = "student_loan"
    MORTGAGE = "mortgage"
    AUTO_LOAN = "auto_loan"
    PERSONAL_LOAN = "personal_loan"
    BUSINESS_LOAN = "business_loan"
    LINE_OF_CREDIT = "line_of_credit"
    MEDICAL_DEBT = "medical_debt"
    OTHER = "other"

class PaymentFrequency(str, enum.Enum):
    WEEKLY = "weekly"
    BI_WEEKLY = "bi_weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"

class DebtStatus(str, enum.Enum):
    CURRENT = "current"
    PAST_DUE = "past_due"
    DEFAULT = "default"
    PAID_OFF = "paid_off"
    IN_COLLECTION = "in_collection"
    SETTLED = "settled"

class Debt(Base):
    """Model for tracking various types of debts and loans."""
    
    __tablename__ = "debts"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(Enum(DebtType), nullable=False)
    status = Column(Enum(DebtStatus), default=DebtStatus.CURRENT)
    
    # Debt amounts
    original_amount = Column(Float, nullable=False)
    current_balance = Column(Float, nullable=False)
    minimum_payment = Column(Float)
    
    # Interest details
    interest_rate = Column(Float, nullable=False)
    interest_type = Column(String)  # Fixed or Variable
    apr = Column(Float)  # Annual Percentage Rate
    
    # Payment schedule
    payment_frequency = Column(Enum(PaymentFrequency), default=PaymentFrequency.MONTHLY)
    payment_amount = Column(Float)
    next_payment_date = Column(DateTime)
    last_payment_date = Column(DateTime)
    last_payment_amount = Column(Float)
    
    # Loan terms
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    term_months = Column(Integer)
    remaining_payments = Column(Integer)
    
    # Lender information
    lender = Column(String)
    account_number = Column(String)
    contact_info = Column(String)
    
    # Collateral (for secured debts)
    is_secured = Column(bool, default=False)
    collateral_type = Column(String)
    collateral_value = Column(Float)
    
    # Tracking and history
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Additional details
    payment_history = Column(Text)  # JSON string of payment history
    late_fees = Column(Float, default=0)
    total_interest_paid = Column(Float, default=0)
    notes = Column(Text)
    tags = Column(String)

    def calculate_total_cost(self) -> float:
        """Calculate the total cost of the debt including interest."""
        if self.original_amount and self.interest_rate and self.term_months:
            monthly_rate = self.interest_rate / 12 / 100
            total = self.original_amount * (1 + monthly_rate) ** self.term_months
            return round(total, 2)
        return self.original_amount

    def calculate_remaining_balance(self) -> float:
        """Calculate the remaining balance based on payments made."""
        return self.current_balance

    def calculate_monthly_payment(self) -> float:
        """Calculate the monthly payment amount."""
        if self.original_amount and self.interest_rate and self.term_months:
            monthly_rate = self.interest_rate / 12 / 100
            payment = (self.original_amount * monthly_rate * (1 + monthly_rate) ** self.term_months) / \
                     ((1 + monthly_rate) ** self.term_months - 1)
            return round(payment, 2)
        return 0

    def calculate_payoff_date(self) -> datetime:
        """Calculate the expected payoff date based on current payment schedule."""
        if self.current_balance and self.payment_amount and self.interest_rate:
            monthly_rate = self.interest_rate / 12 / 100
            months_remaining = -(-monthly_rate + 
                              (monthly_rate ** 2 + 2 * monthly_rate * self.current_balance / self.payment_amount) ** 0.5) / \
                             monthly_rate
            return datetime.now() + timedelta(days=30 * months_remaining)
        return self.end_date

    def calculate_debt_to_income_ratio(self, monthly_income: float) -> float:
        """Calculate debt-to-income ratio."""
        if monthly_income and monthly_income > 0:
            monthly_payment = self.calculate_monthly_payment()
            return (monthly_payment / monthly_income) * 100
        return 0

    def is_past_due(self) -> bool:
        """Check if the debt is past due."""
        if self.next_payment_date:
            return datetime.now() > self.next_payment_date
        return False

    def add_payment(self, amount: float, date: datetime = None) -> None:
        """Record a new payment."""
        if not date:
            date = datetime.now()
        
        self.last_payment_date = date
        self.last_payment_amount = amount
        self.current_balance -= amount
        
        # Update payment history
        payment_history = self.get_payment_history()
        payment_history.append({
            "date": date.isoformat(),
            "amount": amount,
            "balance": self.current_balance
        })
        self.payment_history = json.dumps(payment_history)
        
        # Update next payment date
        if self.payment_frequency == PaymentFrequency.MONTHLY:
            self.next_payment_date = date + timedelta(days=30)
        elif self.payment_frequency == PaymentFrequency.BI_WEEKLY:
            self.next_payment_date = date + timedelta(days=14)
        elif self.payment_frequency == PaymentFrequency.WEEKLY:
            self.next_payment_date = date + timedelta(days=7)

    def get_payment_history(self) -> list:
        """Get the payment history as a list."""
        if self.payment_history:
            return json.loads(self.payment_history)
        return []

    def to_dict(self) -> dict:
        """Convert debt to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "original_amount": self.original_amount,
            "current_balance": self.current_balance,
            "interest_rate": self.interest_rate,
            "payment_frequency": self.payment_frequency,
            "payment_amount": self.payment_amount,
            "next_payment_date": self.next_payment_date.isoformat() if self.next_payment_date else None,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "lender": self.lender,
            "minimum_payment": self.minimum_payment,
            "total_interest_paid": self.total_interest_paid,
            "remaining_payments": self.remaining_payments,
            "is_past_due": self.is_past_due(),
            "payment_history": self.get_payment_history(),
            "notes": self.notes,
            "tags": self.tags
        }
