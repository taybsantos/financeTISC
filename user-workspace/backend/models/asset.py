from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.sql import func
import enum

from backend.config.database import Base

class AssetType(str, enum.Enum):
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

class AssetStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SOLD = "sold"

class Asset(Base):
    """Model for tracking various types of assets."""
    
    __tablename__ = "assets"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(Enum(AssetType), nullable=False)
    value = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    status = Column(Enum(AssetStatus), default=AssetStatus.ACTIVE)
    
    # Asset details
    description = Column(Text)
    acquisition_date = Column(DateTime)
    acquisition_value = Column(Float)
    current_value = Column(Float)
    last_valuation_date = Column(DateTime)
    
    # Location/identification
    institution = Column(String)  # Bank, broker, etc.
    account_number = Column(String)
    location = Column(String)  # Physical location for real estate, etc.
    
    # Investment specific
    quantity = Column(Float)  # Number of shares, units, etc.
    ticker_symbol = Column(String)  # For stocks, ETFs, etc.
    interest_rate = Column(Float)  # For interest-bearing assets
    maturity_date = Column(DateTime)  # For bonds, CDs, etc.
    
    # Real estate specific
    property_type = Column(String)  # Residential, Commercial, etc.
    address = Column(Text)
    square_footage = Column(Float)
    
    # Ownership and tracking
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Risk assessment
    risk_level = Column(String)  # Low, Medium, High
    liquidity_level = Column(String)  # High, Medium, Low
    
    # Performance tracking
    annual_return = Column(Float)
    total_return = Column(Float)
    unrealized_gain_loss = Column(Float)
    
    # Notes and tags
    notes = Column(Text)
    tags = Column(String)  # Comma-separated tags

    def calculate_current_value(self) -> float:
        """Calculate the current value of the asset."""
        if self.type in [AssetType.STOCK, AssetType.ETF]:
            # Would integrate with market data API
            return self.quantity * self.current_value
        elif self.type == AssetType.REAL_ESTATE:
            # Could integrate with real estate valuation API
            return self.current_value
        return self.value

    def calculate_return(self) -> float:
        """Calculate the return on investment."""
        if self.acquisition_value and self.acquisition_value > 0:
            current = self.calculate_current_value()
            return ((current - self.acquisition_value) / self.acquisition_value) * 100
        return 0

    def calculate_unrealized_gain_loss(self) -> float:
        """Calculate unrealized gain/loss."""
        if self.acquisition_value:
            return self.calculate_current_value() - self.acquisition_value
        return 0

    def to_dict(self) -> dict:
        """Convert asset to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "value": self.value,
            "currency": self.currency,
            "status": self.status,
            "description": self.description,
            "acquisition_date": self.acquisition_date.isoformat() if self.acquisition_date else None,
            "current_value": self.current_value,
            "last_valuation_date": self.last_valuation_date.isoformat() if self.last_valuation_date else None,
            "institution": self.institution,
            "risk_level": self.risk_level,
            "liquidity_level": self.liquidity_level,
            "annual_return": self.annual_return,
            "total_return": self.total_return,
            "unrealized_gain_loss": self.unrealized_gain_loss,
            "notes": self.notes,
            "tags": self.tags
        }
