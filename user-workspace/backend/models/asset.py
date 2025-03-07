from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Text, Boolean
from sqlalchemy.orm import relationship
from backend.config.database import Base

class AssetType(str, Enum):
    CASH = "cash"
    BANK_ACCOUNT = "bank_account"
    INVESTMENT = "investment"
    REAL_ESTATE = "real_estate"
    VEHICLE = "vehicle"
    CRYPTOCURRENCY = "cryptocurrency"
    STOCK = "stock"
    BOND = "bond"
    MUTUAL_FUND = "mutual_fund"
    ETF = "etf"
    RETIREMENT = "retirement"
    OTHER = "other"

class AssetStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SOLD = "sold"

class Asset(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(SQLEnum(AssetType), nullable=False, index=True)
    value = Column(Float, nullable=False)
    currency = Column(String)
    status = Column(SQLEnum(AssetStatus), default=AssetStatus.ACTIVE)
    description = Column(Text)
    
    # Acquisition details
    acquisition_date = Column(DateTime)
    acquisition_value = Column(Float)
    current_value = Column(Float)
    last_valuation_date = Column(DateTime)
    
    # Financial details
    institution = Column(String)
    account_number = Column(String)
    location = Column(String)
    quantity = Column(Float)
    ticker_symbol = Column(String)
    interest_rate = Column(Float)
    maturity_date = Column(DateTime)
    
    # Real estate specific
    property_type = Column(String)
    address = Column(Text)
    square_footage = Column(Float)
    
    # Investment specific
    risk_level = Column(String)
    liquidity_level = Column(String)
    annual_return = Column(Float)
    total_return = Column(Float)
    unrealized_gain_loss = Column(Float)
    
    # Metadata
    notes = Column(Text)
    tags = Column(String)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="assets")

    def __repr__(self):
        return f"<Asset {self.name}: {self.type} - {self.current_value}>"

    def calculate_current_value(self):
        """Calculate the current value of the asset."""
        if self.current_value is not None:
            return self.current_value
        return self.value

    def calculate_return(self):
        """Calculate the return on investment."""
        if self.acquisition_value and self.current_value:
            return ((self.current_value - self.acquisition_value) / self.acquisition_value) * 100
        return 0

    @property
    def tags_list(self):
        """Return tags as a list."""
        return [tag.strip() for tag in self.tags.split(",")] if self.tags else []

    @tags_list.setter
    def tags_list(self, tags):
        """Set tags from a list."""
        self.tags = ",".join(tags) if tags else None
