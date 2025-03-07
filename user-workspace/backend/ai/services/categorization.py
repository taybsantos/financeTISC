from typing import Dict, List, Optional
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sqlalchemy.orm import Session

from backend.models.transaction import Transaction
from backend.models.user import Category

class TransactionCategorizer:
    def __init__(self):
        """Initialize the categorizer with NLP models."""
        # Load spaCy model for text processing
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            # Download if not available
            spacy.cli.download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        self.vectorizer = TfidfVectorizer(
            analyzer='word',
            ngram_range=(1, 2),
            stop_words='english',
            max_features=5000
        )
        
        self.classifier = MultinomialNB()
        self.is_trained = False

    def preprocess_text(self, text: str) -> str:
        """Preprocess transaction description for better categorization."""
        # Convert to lowercase and process with spaCy
        doc = self.nlp(text.lower())
        
        # Extract relevant tokens (nouns, verbs, proper nouns)
        tokens = [
            token.text for token in doc
            if (token.pos_ in ['NOUN', 'VERB', 'PROPN'] and
                not token.is_stop and
                token.is_alpha)
        ]
        
        return ' '.join(tokens)

    def train(self, transactions: List[Transaction]):
        """Train the categorizer using historical transactions."""
        if not transactions:
            return
        
        # Prepare training data
        descriptions = [
            self.preprocess_text(t.description)
            for t in transactions
            if t.description and t.category_id
        ]
        
        categories = [
            t.category_id
            for t in transactions
            if t.description and t.category_id
        ]
        
        if not descriptions or not categories:
            return
        
        # Transform text to TF-IDF features
        X = self.vectorizer.fit_transform(descriptions)
        
        # Train the classifier
        self.classifier.fit(X, categories)
        self.is_trained = True

    def predict_category(self, description: str) -> Optional[str]:
        """Predict category for a new transaction description."""
        if not self.is_trained:
            return None
        
        # Preprocess and vectorize the description
        processed_text = self.preprocess_text(description)
        X = self.vectorizer.transform([processed_text])
        
        # Predict category
        try:
            category_id = self.classifier.predict(X)[0]
            return category_id
        except:
            return None

    def get_confidence_scores(self, description: str) -> Dict[str, float]:
        """Get confidence scores for each category."""
        if not self.is_trained:
            return {}
        
        # Preprocess and vectorize the description
        processed_text = self.preprocess_text(description)
        X = self.vectorizer.transform([processed_text])
        
        # Get probability scores
        try:
            probabilities = self.classifier.predict_proba(X)[0]
            return dict(zip(self.classifier.classes_, probabilities))
        except:
            return {}

def setup_default_categories(db: Session, user_id: str) -> List[Category]:
    """Set up default transaction categories for a new user."""
    default_categories = [
        {"name": "Housing", "description": "Rent, mortgage, utilities, maintenance"},
        {"name": "Transportation", "description": "Car payments, fuel, public transit, maintenance"},
        {"name": "Food", "description": "Groceries, dining out, delivery"},
        {"name": "Healthcare", "description": "Medical expenses, insurance, medications"},
        {"name": "Entertainment", "description": "Movies, games, hobbies, subscriptions"},
        {"name": "Shopping", "description": "Clothing, electronics, household items"},
        {"name": "Education", "description": "Tuition, books, courses, training"},
        {"name": "Personal Care", "description": "Haircuts, gym, beauty products"},
        {"name": "Insurance", "description": "Life, home, auto insurance"},
        {"name": "Savings", "description": "Emergency fund, investments"},
        {"name": "Debt Payments", "description": "Credit card, loan payments"},
        {"name": "Income", "description": "Salary, investments, other income"},
        {"name": "Gifts", "description": "Presents, donations, charity"},
        {"name": "Travel", "description": "Flights, hotels, vacation expenses"},
        {"name": "Business", "description": "Work-related expenses"},
        {"name": "Other", "description": "Miscellaneous expenses"}
    ]
    
    categories = []
    for cat in default_categories:
        category = Category(
            name=cat["name"],
            description=cat["description"],
            user_id=user_id
        )
        db.add(category)
        categories.append(category)
    
    db.commit()
    return categories

def get_or_create_categorizer(db: Session, user_id: str) -> TransactionCategorizer:
    """Get or create a transaction categorizer for a user."""
    # Create categorizer
    categorizer = TransactionCategorizer()
    
    # Get user's transactions with categories
    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == user_id,
            Transaction.category_id.isnot(None)
        )
        .all()
    )
    
    # Train categorizer if there are enough transactions
    if len(transactions) >= 10:
        categorizer.train(transactions)
    
    return categorizer

def categorize_transaction(
    db: Session,
    user_id: str,
    description: str,
    amount: float
) -> Dict:
    """Categorize a transaction based on its description and amount."""
    # Get or create categorizer
    categorizer = get_or_create_categorizer(db, user_id)
    
    # Get prediction and confidence scores
    category_id = categorizer.predict_category(description)
    confidence_scores = categorizer.get_confidence_scores(description)
    
    # Get category details if predicted
    category = None
    if category_id:
        category = db.query(Category).filter(
            Category.id == category_id,
            Category.user_id == user_id
        ).first()
    
    return {
        "category_id": category_id,
        "category_name": category.name if category else None,
        "confidence": confidence_scores.get(category_id, 0) if category_id else 0,
        "alternative_categories": [
            {
                "category_id": cat_id,
                "confidence": score
            }
            for cat_id, score in confidence_scores.items()
            if cat_id != category_id
        ]
    }

def bulk_categorize_transactions(
    db: Session,
    user_id: str,
    transactions: List[Dict]
) -> List[Dict]:
    """Categorize multiple transactions in bulk."""
    categorizer = get_or_create_categorizer(db, user_id)
    
    results = []
    for transaction in transactions:
        result = categorize_transaction(
            db,
            user_id,
            transaction["description"],
            transaction["amount"]
        )
        results.append({
            **transaction,
            **result
        })
    
    return results
