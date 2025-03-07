import uvicorn
from app.main import app
from config.settings import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Main function to run the FastAPI application
    """
    logger.info(f"Starting {settings.PROJECT_NAME} API server...")
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,  # Enable auto-reload during development
            log_level="info",
            access_log=True,
        )
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        raise

if __name__ == "__main__":
    main()
