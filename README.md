# FixMyResume

AI-powered resume analysis and job application tracking platform.

## Project Structure

```
FixMyResume/
├── backend/          # FastAPI + SQLAlchemy + Alembic
│   ├── app/
│   │   ├── api/      # API routes (v1)
│   │   ├── core/     # Configuration
│   │   ├── database/ # SQLAlchemy setup
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # Business logic
│   │   ├── repositories/ # Data access layer
│   │   ├── analysis/ # Resume analysis
│   │   └── utils/    # Utilities
│   ├── alembic/      # Database migrations
│   ├── tests/        # Backend tests
│   └── requirements.txt
├── frontend/         # React + Vite + Tailwind CSS
│   └── src/
│       ├── api/      # Axios API client
│       ├── components/ # Reusable components
│       ├── pages/    # Page components
│       ├── hooks/    # Custom hooks
│       ├── context/  # React context
│       ├── ui/       # UI components
│       └── types/    # TypeScript types
└── docs/             # Documentation
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm

## Backend Setup

```bash
cd backend

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload
```

The backend will be available at `http://localhost:8000`.

### Backend Endpoints

- `GET /` - Root endpoint
- `GET /test-db` - Database connection test
- `GET /api/v1/health` - Health check (API + database status)
- `GET /docs` - Swagger UI documentation

### Running Backend Tests

```bash
cd backend
venv\Scripts\python -m pytest tests -v
```

## Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:5173`.

### Frontend Build

```bash
cd frontend
npm run build
```

## Database Configuration

The application uses environment variables for database configuration. By default, it uses SQLite for local development.

### SQLite (default)

```
DATABASE_URL=sqlite:///./fixmyresume.db
```

### PostgreSQL (when ready)

```
DATABASE_URL=postgresql://user:password@localhost:5432/fixmyresume
```

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection URL | `sqlite:///./fixmyresume.db` |
| `APP_NAME` | Application name | `FixMyResume` |
| `APP_VERSION` | Application version | `0.1.0` |
| `DEBUG` | Debug mode | `false` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:5173,http://127.0.0.1:5173` |

### Frontend (`frontend/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API base URL | `http://localhost:8000` |

## Development

- Backend runs on port `8000`
- Frontend runs on port `5173`
- CORS is configured to allow the frontend to communicate with the backend