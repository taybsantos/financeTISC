import spacy
from typing import Optional, Dict, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TransactionCategorizer:
    """Service for automatically categorizing financial transactions using NLP."""
    
    def __init__(self):
        """Initialize the categorizer with spaCy model."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("Downloading spaCy model...")
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        # Pre-defined category mappings
        self.category_keywords = {
            "food": ["restaurant", "cafe", "grocery", "food", "meal", "dinner", "lunch"],
            "transport": ["uber", "lyft", "taxi", "bus", "train", "gas", "fuel"],
            "shopping": ["amazon", "walmart", "target", "store", "shop"],
            "utilities": ["electricity", "water", "gas", "internet", "phone"],
            "entertainment": ["netflix", "spotify", "movie", "game", "subscription"],
        }

    def categorize(self, description: str) -> Optional[str]:
        """
        Categorize a transaction based on its description.
        
        Args:
            description (str): The transaction description
            
        Returns:
            Optional[str]: The predicted category or None if uncertain
        """
        try:
            # Preprocess description
            description = description.lower().strip()
            doc = self.nlp(description)
            
            # Extract relevant tokens
            tokens = [token.text for token in doc if not token.is_stop and token.is_alpha]
            
            # Match against category keywords
            scores = {category: 0 for category in self.category_keywords}
            
            for token in tokens:
                for category, keywords in self.category_keywords.items():
                    if token in keywords:
                        scores[category] += 1
            
            # Get category with highest score
            max_score = max(scores.values())
            if max_score > 0:
                return max(scores.items(), key=lambda x: x[1])[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error categorizing transaction: {str(e)}")
            return None

    def train_on_historical_data(self, transactions: List[Dict]):
        """
        Train the categorizer using historical transaction data.
        
        Args:
            transactions (List[Dict]): List of historical transactions with 
                                     confirmed categories
        """
        try:
            # Update category keywords based on historical data
            for transaction in transactions:
                if transaction.get('category') and transaction.get('description'):
                    category = transaction['category']
                    description = transaction['description'].lower()
                    
                    # Extract significant terms
                    doc = self.nlp(description)
                    terms = [token.text for token in doc 
                            if not token.is_stop and token.is_alpha]
                    
                    # Add terms to category keywords
                    if category not in self.category_keywords:
                        self.category_keywords[category] = []
                    self.category_keywords[category].extend(terms)
            
            # Remove duplicates
            self.category_keywords = {
                category: list(set(keywords))
                for category, keywords in self.category_keywords.items()
            }
            
            logger.info(f"Updated categorizer with {len(transactions)} transactions")
            
        except Exception as e:
            logger.error(f"Error training categorizer: {str(e)}")

    def get_confidence_score(self, description: str, category: str) -> float:
        """
        Calculate confidence score for a category prediction.
        
        Args:
            description (str): Transaction description
            category (str): Predicted category
            
        Returns:
            float: Confidence score between 0 and 1
        """
        try:
            description = description.lower().strip()
            doc = self.nlp(description)
            tokens = [token.text for token in doc if not token.is_stop and token.is_alpha]
            
            if category not in self.category_keywords:
                return 0.0
            
            matches = sum(1 for token in tokens 
                         if token in self.category_keywords[category])
            
            # Calculate confidence based on keyword matches
            confidence = matches / len(tokens) if tokens else 0.0
            
            return min(confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating confidence score: {str(e)}")
            return 0.0
