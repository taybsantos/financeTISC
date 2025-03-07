from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.config.database import Base
import enum
import uuid

class TransactionType(enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"

class TransactionStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    amount = Column(Float, nullable=False)
    description = Column(String)
    type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    
    # Foreign keys
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    category_id = Column(String, ForeignKey("categories.id"))
    
    # Metadata
    transaction_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Optional fields for transfers
    source_account = Column(String)
    destination_account = Column(String)
    
    # Additional metadata
    tags = Column(String)  # Stored as comma-separated values
    notes = Column(String)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction {self.id}: {self.amount} - {self.type.value}>"

    @property
    def tags_list(self):
        """Convert tags string to list"""
        return [tag.strip() for tag in self.tags.split(',')] if self.tags else []

    @tags_list.setter
    def tags_list(self, tags):
        """Convert list of tags to string"""
        self.tags = ','.join(tags) if tags else None
