# Backend API

This is the backend API for the dashboard agent project, built with Flask.

## Project Structure

```
backend/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create from .env.example)
└── api/               # API routes and controllers
    ├── __init__.py
    ├── auth.py        # Authentication routes
    ├── data.py        # Data processing routes
    └── ai.py          # AI/OpenAI integration routes
```

## Setup Instructions

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - Unix/MacOS:
     ```bash
     source venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` with your actual configuration values.

5. Run the development server:
   ```bash
   python app.py
   ```

The server will start on http://localhost:5000 by default.

## API Endpoints

- `GET /api/health` - Health check endpoint
- More endpoints will be added as needed

## Environment Variables

See `.env.example` for required environment variables. 