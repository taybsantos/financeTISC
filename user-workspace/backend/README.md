# FinanciaAI Backend

A FastAPI-based backend for the FinanciaAI personal finance management platform with AI integration.

## Features

- User authentication with JWT tokens
- Transaction management with categories
- AI-powered financial insights (coming soon)
- RESTful API design
- PostgreSQL database
- Comprehensive error handling
- Environment-based configuration

## Prerequisites

- Python 3.8+
- PostgreSQL
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd financiaai/backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
# Create PostgreSQL database
createdb financiaai
```

5. Configure environment variables:
- Copy `.env.example` to `.env`
- Update the values in `.env` with your configuration

## Running the Application

1. Activate the virtual environment (if not already activated):
```bash
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

2. Run the application:
```bash
python run.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:
- Interactive API documentation: `http://localhost:8000/docs`
- Alternative API documentation: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- POST `/api/v1/auth/register` - Register a new user
- POST `/api/v1/auth/token` - Login and get access token
- GET `/api/v1/auth/me` - Get current user information

### Transactions
- GET `/api/v1/transactions` - List transactions
- POST `/api/v1/transactions` - Create a new transaction
- GET `/api/v1/transactions/{id}` - Get transaction details
- PUT `/api/v1/transactions/{id}` - Update a transaction
- DELETE `/api/v1/transactions/{id}` - Delete a transaction

### Categories
- GET `/api/v1/transactions/categories` - List categories
- POST `/api/v1/transactions/categories` - Create a new category

## Development

### Project Structure
```
backend/
├── app/
│   └── main.py          # FastAPI application instance
├── config/
│   ├── database.py      # Database configuration
│   └── settings.py      # Application settings
├── models/
│   ├── user.py          # User and Category models
│   └── transaction.py   # Transaction model
├── routers/
│   ├── auth.py          # Authentication endpoints
│   └── transactions.py  # Transaction endpoints
├── requirements.txt     # Project dependencies
├── .env                 # Environment variables
└── run.py              # Application entry point
```

### Running Tests
```bash
# Coming soon
pytest
```

## Security

- JWT-based authentication
- Password hashing with bcrypt
- Environment-based configuration
- CORS protection
- Input validation with Pydantic

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
