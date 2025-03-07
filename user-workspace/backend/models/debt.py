from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Text, Boolean, Integer
from sqlalchemy.orm import relationship
from backend.config.database import Base

class DebtType(str, Enum):
    CREDIT_CARD = "credit_card"
    STUDENT_LOAN = "student_loan"
    MORTGAGE = "mortgage"
    AUTO_LOAN = "auto_loan"
    PERSONAL_LOAN = "personal_loan"
    BUSINESS_LOAN = "business_loan"
    LINE_OF_CREDIT = "line_of_credit"
    MEDICAL_DEBT = "medical_debt"
    OTHER = "other"

class DebtStatus(str, Enum):
    CURRENT = "current"
    PAST_DUE = "past_due"
    DEFAULT = "default"
    PAID_OFF = "paid_off"
    IN_COLLECTION = "in_collection"
    SETTLED = "settled"

class PaymentFrequency(str, Enum):
    WEEKLY = "weekly"
    BI_WEEKLY = "bi_weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"

class Debt(Base):
    __tablename__ = "debts"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(SQLEnum(DebtType), nullable=False, index=True)
    status = Column(SQLEnum(DebtStatus), default=DebtStatus.CURRENT)
    
    # Amount details
    original_amount = Column(Float, nullable=False)
    current_balance = Column(Float, nullable=False)
    minimum_payment = Column(Float)
    
    # Interest details
    interest_rate = Column(Float, nullable=False)
    interest_type = Column(String)  # Fixed or Variable
    apr = Column(Float)
    
    # Payment details
    payment_frequency = Column(SQLEnum(PaymentFrequency), default=PaymentFrequency.MONTHLY)
    payment_amount = Column(Float)
    next_payment_date = Column(DateTime)
    last_payment_date = Column(DateTime)
    last_payment_amount = Column(Float)
    
    # Term details
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    term_months = Column(Integer)
    remaining_payments = Column(Integer)
    
    # Lender details
    lender = Column(String)
    account_number = Column(String)
    contact_info = Column(String)
    
    # Security details
    is_secured = Column(Boolean, default=False)
    collateral_type = Column(String)
    collateral_value = Column(Float)
    
    # History and tracking
    payment_history = Column(Text)  # JSON string of payment history
    late_fees = Column(Float, default=0)
    total_interest_paid = Column(Float, default=0)
    
    # Metadata
    notes = Column(Text)
    tags = Column(String)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="debts")

    def __repr__(self):
        return f"<Debt {self.name}: {self.type} - {self.current_balance}>"

    def calculate_total_payoff_amount(self):
        """Calculate the total amount needed to pay off the debt."""
        return self.current_balance + (self.late_fees or 0)

    def calculate_total_cost(self):
        """Calculate the total cost of the debt including interest."""
        return self.original_amount + (self.total_interest_paid or 0) + (self.late_fees or 0)

    def is_past_due(self):
        """Check if the debt is past due."""
        if not self.next_payment_date:
            return False
        return self.next_payment_date < datetime.utcnow() and self.status != DebtStatus.PAID_OFF

    @property
    def tags_list(self):
        """Return tags as a list."""
        return [tag.strip() for tag in self.tags.split(",")] if self.tags else []

    @tags_list.setter
    def tags_list(self, tags):
        """Set tags from a list."""
        self.tags = ",".join(tags) if tags else None
