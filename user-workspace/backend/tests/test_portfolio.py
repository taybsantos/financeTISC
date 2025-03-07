import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import uuid

from backend.models.asset import Asset, AssetType, AssetStatus
from backend.models.debt import Debt, DebtType, DebtStatus, PaymentFrequency
from backend.app.main import app

@pytest.fixture
def test_asset():
    return {
        "name": "Test Investment",
        "type": AssetType.INVESTMENT,
        "value": 10000.0,
        "currency": "USD",
        "status": AssetStatus.ACTIVE,
        "description": "Test investment asset",
        "acquisition_date": datetime.now().isoformat(),
        "acquisition_value": 9000.0,
        "current_value": 10000.0,
        "institution": "Test Bank",
        "risk_level": "medium",
        "annual_return": 10.0
    }

@pytest.fixture
def test_debt():
    return {
        "name": "Test Loan",
        "type": DebtType.PERSONAL_LOAN,
        "status": DebtStatus.CURRENT,
        "original_amount": 20000.0,
        "current_balance": 15000.0,
        "interest_rate": 5.5,
        "payment_frequency": PaymentFrequency.MONTHLY,
        "payment_amount": 500.0,
        "start_date": datetime.now().isoformat(),
        "term_months": 48,
        "lender": "Test Bank"
    }

def test_create_asset(client: TestClient, test_db: Session, test_user_token: str, test_asset: dict):
    response = client.post(
        "/api/v1/portfolio/assets",
        json=test_asset,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_asset["name"]
    assert data["type"] == test_asset["type"]
    assert data["value"] == test_asset["value"]

def test_get_assets(client: TestClient, test_db: Session, test_user_token: str, test_asset: dict):
    # Create test asset first
    client.post(
        "/api/v1/portfolio/assets",
        json=test_asset,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    response = client.get(
        "/api/v1/portfolio/assets",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == test_asset["name"]

def test_create_debt(client: TestClient, test_db: Session, test_user_token: str, test_debt: dict):
    response = client.post(
        "/api/v1/portfolio/debts",
        json=test_debt,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_debt["name"]
    assert data["type"] == test_debt["type"]
    assert data["current_balance"] == test_debt["current_balance"]

def test_get_debts(client: TestClient, test_db: Session, test_user_token: str, test_debt: dict):
    # Create test debt first
    client.post(
        "/api/v1/portfolio/debts",
        json=test_debt,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    response = client.get(
        "/api/v1/portfolio/debts",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == test_debt["name"]

def test_get_net_worth(client: TestClient, test_db: Session, test_user_token: str, test_asset: dict, test_debt: dict):
    # Create test asset and debt
    client.post(
        "/api/v1/portfolio/assets",
        json=test_asset,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    client.post(
        "/api/v1/portfolio/debts",
        json=test_debt,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    response = client.get(
        "/api/v1/portfolio/analysis/net-worth",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_assets" in data
    assert "total_debts" in data
    assert "net_worth" in data
    assert data["net_worth"] == data["total_assets"] - data["total_debts"]

def test_get_portfolio_projections(client: TestClient, test_db: Session, test_user_token: str, test_asset: dict, test_debt: dict):
    # Create test asset and debt
    client.post(
        "/api/v1/portfolio/assets",
        json=test_asset,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    client.post(
        "/api/v1/portfolio/debts",
        json=test_debt,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    response = client.get(
        "/api/v1/portfolio/analysis/projections",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "monthly_projections" in data
    assert "current_net_worth" in data
    assert len(data["monthly_projections"]) > 0

def test_get_debt_overview(client: TestClient, test_db: Session, test_user_token: str, test_debt: dict):
    # Create test debt
    client.post(
        "/api/v1/portfolio/debts",
        json=test_debt,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    response = client.get(
        "/api/v1/portfolio/analysis/debt-overview",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_debt" in data
    assert "monthly_payments" in data
    assert "average_interest_rate" in data
    assert "debt_types" in data
    assert data["total_debt"] == test_debt["current_balance"]

def test_update_asset(client: TestClient, test_db: Session, test_user_token: str, test_asset: dict):
    # Create test asset first
    create_response = client.post(
        "/api/v1/portfolio/assets",
        json=test_asset,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    asset_id = create_response.json()["id"]
    
    # Update the asset
    updated_data = {
        "value": 12000.0,
        "current_value": 12000.0,
        "last_valuation_date": datetime.now().isoformat()
    }
    
    response = client.put(
        f"/api/v1/portfolio/assets/{asset_id}",
        json=updated_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["value"] == updated_data["value"]
    assert data["current_value"] == updated_data["current_value"]

def test_update_debt(client: TestClient, test_db: Session, test_user_token: str, test_debt: dict):
    # Create test debt first
    create_response = client.post(
        "/api/v1/portfolio/debts",
        json=test_debt,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    debt_id = create_response.json()["id"]
    
    # Update the debt
    updated_data = {
        "current_balance": 14000.0,
        "last_payment_amount": 1000.0,
        "last_payment_date": datetime.now().isoformat()
    }
    
    response = client.put(
        f"/api/v1/portfolio/debts/{debt_id}",
        json=updated_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["current_balance"] == updated_data["current_balance"]
    assert data["last_payment_amount"] == updated_data["last_payment_amount"]

def test_delete_asset(client: TestClient, test_db: Session, test_user_token: str, test_asset: dict):
    # Create test asset first
    create_response = client.post(
        "/api/v1/portfolio/assets",
        json=test_asset,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    asset_id = create_response.json()["id"]
    
    # Delete the asset
    response = client.delete(
        f"/api/v1/portfolio/assets/{asset_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    
    # Verify asset is deleted
    get_response = client.get(
        f"/api/v1/portfolio/assets/{asset_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert get_response.status_code == 404

def test_delete_debt(client: TestClient, test_db: Session, test_user_token: str, test_debt: dict):
    # Create test debt first
    create_response = client.post(
        "/api/v1/portfolio/debts",
        json=test_debt,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    debt_id = create_response.json()["id"]
    
    # Delete the debt
    response = client.delete(
        f"/api/v1/portfolio/debts/{debt_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    
    # Verify debt is deleted
    get_response = client.get(
        f"/api/v1/portfolio/debts/{debt_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert get_response.status_code == 404
