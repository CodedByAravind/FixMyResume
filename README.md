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
- `GET /api/v1/resumes` - List authenticated user's resumes
- `POST /api/v1/resumes` - Create a resume
- `GET /api/v1/resumes/{id}` - Get a resume (own only)
- `PUT /api/v1/resumes/{id}` - Update a resume (own only)
- `DELETE /api/v1/resumes/{id}` - Delete a resume (own only)
- `POST/PUT/DELETE /api/v1/resumes/{id}/education|experience|projects|skills|certifications` - Manage resume sections
- `POST /api/v1/resumes/{id}/analyze` - Analyze a resume against a job description (rule-based, provider-agnostic)
- `POST /api/v1/resumes/{id}/tailor` - Create a tailored version (source + tailored snapshots)
- `GET /api/v1/resumes/{id}/versions` - List versions
- `GET /api/v1/resumes/{id}/versions/{vid}` - View a version
- `GET /api/v1/resumes/{id}/versions/{vid}/compare` - Compare source vs tailored
- `DELETE /api/v1/resumes/{id}/versions/{vid}` - Delete a version
- `GET /docs` - Swagger UI documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/register` | Register a new user (auto-login, returns token pair) |
| `POST` | `/api/v1/auth/login` | Log in and receive an access + refresh token pair |
| `POST` | `/api/v1/auth/refresh` | Rotate a refresh token and get a new token pair |
| `POST` | `/api/v1/auth/logout` | Revoke the given refresh token |
| `GET` | `/api/v1/auth/me` | Get the current authenticated user (requires Bearer token) |

Authentication uses short-lived JWT access tokens (30 min) and long-lived, revocable
opaque refresh tokens (7 days) that are rotated on every refresh. Only SHA-256 hashes of
refresh tokens are stored in the database; raw tokens and plaintext passwords are never stored.

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
| `SECRET_KEY` | JWT signing secret (use long random value in prod) | `change-me-in-production-with-a-long-random-string` |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime (minutes) | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime (days) | `7` |

### Frontend (`frontend/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API base URL | `http://localhost:8000` |

## Development

- Backend runs on port `8000`
- Frontend runs on port `5173`
- CORS is configured to allow the frontend to communicate with the backend
