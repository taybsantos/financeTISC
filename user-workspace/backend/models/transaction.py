from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from backend.config.database import Base

class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String)
    type = Column(SQLEnum(TransactionType), nullable=False)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(String, ForeignKey("categories.id", ondelete="SET NULL"), index=True)
    transaction_date = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    source_account = Column(String)
    destination_account = Column(String)
    tags = Column(String)
    notes = Column(String)

    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction {self.id}: {self.amount} - {self.type}>"

    @property
    def tags_list(self):
        return [tag.strip() for tag in self.tags.split(",")] if self.tags else []

    @tags_list.setter
    def tags_list(self, tags):
        self.tags = ",".join(tags) if tags else None
