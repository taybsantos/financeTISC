import asyncio
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid

from backend.config.database import engine, SessionLocal
from backend.models.user import Category
from backend.config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default categories
DEFAULT_CATEGORIES = [
    {
        "name": "Housing",
        "description": "Rent, mortgage, utilities, maintenance"
    },
    {
        "name": "Transportation",
        "description": "Car payments, fuel, public transit, maintenance"
    },
    {
        "name": "Food",
        "description": "Groceries, dining out, snacks"
    },
    {
        "name": "Healthcare",
        "description": "Medical bills, medications, insurance"
    },
    {
        "name": "Entertainment",
        "description": "Movies, games, hobbies, subscriptions"
    },
    {
        "name": "Shopping",
        "description": "Clothing, electronics, personal items"
    },
    {
        "name": "Education",
        "description": "Tuition, books, courses, training"
    },
    {
        "name": "Savings",
        "description": "Emergency fund, investments, retirement"
    },
    {
        "name": "Income",
        "description": "Salary, freelance work, investments"
    },
    {
        "name": "Other",
        "description": "Miscellaneous expenses"
    }
]

def init_db() -> None:
    try:
        # Create database if it doesn't exist
        with engine.connect() as connection:
            connection.execute(text("CREATE DATABASE IF NOT EXISTS financiaai"))
            logger.info("Database 'financiaai' created or already exists")
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        return

    try:
        # Create a system user for default categories
        db = SessionLocal()
        
        # Check if system user exists
        system_user_id = str(uuid.uuid4())
        
        # Create default categories
        for category_data in DEFAULT_CATEGORIES:
            category = Category(
                id=str(uuid.uuid4()),
                name=category_data["name"],
                description=category_data["description"],
                user_id=system_user_id
            )
            db.add(category)
        
        db.commit()
        logger.info("Default categories created successfully")
        
    except Exception as e:
        logger.error(f"Error creating default categories: {e}")
        db.rollback()
    finally:
        db.close()

def main() -> None:
    logger.info("Creating initial database...")
    init_db()
    logger.info("Database initialization completed")

if __name__ == "__main__":
    main()
