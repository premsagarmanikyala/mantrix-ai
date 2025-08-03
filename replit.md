# Mantrix - Full-Stack Monorepo

## Project Overview
Mantrix is a comprehensive full-stack monorepo scaffolding with FastAPI backend and React TypeScript frontend, designed for scalable web application development.

## Architecture
- **Backend**: FastAPI (Python 3.11) with SQLAlchemy ORM
- **Frontend**: React 18 with TypeScript, Tailwind CSS
- **Database**: PostgreSQL (Neon database with psycopg2-binary driver)
- **Infrastructure**: Docker containerization with nginx reverse proxy
- **CI/CD**: GitHub Actions pipeline

## Project Structure
```
mantrix/
├── apps/
│   ├── backend/          # FastAPI Python backend
│   │   ├── api/          # Route handlers
│   │   ├── models/       # Pydantic schemas & DB models
│   │   ├── core/         # Configuration & database setup
│   │   ├── services/     # Business logic (AI, users, projects)
│   │   ├── tests/        # Unit tests
│   │   └── main.py       # FastAPI application entry point
│   └── frontend/         # React TypeScript frontend
│       ├── src/
│       │   ├── components/
│       │   ├── pages/
│       │   └── lib/
│       └── package.json
├── infra/               # Docker & infrastructure
└── .github/workflows/   # CI/CD pipelines
```

## Current Status
- ✅ Complete monorepo structure implemented
- ✅ FastAPI backend with SQLAlchemy models
- ✅ React frontend with TypeScript and Tailwind CSS
- ✅ Database tables created successfully (PostgreSQL)
- ✅ PostgreSQL database migration completed with Neon
- ✅ Docker infrastructure configured
- ✅ GitHub Actions CI/CD pipeline
- ✅ Comprehensive documentation

## Key Features
- User management system
- Project management
- AI-powered roadmap generation using OpenAI GPT-4 and LangChain
- Intelligent fallback system for robust roadmap generation
- AI services for resume generation and roadmap planning
- RESTful API with automatic documentation
- Modern React frontend with routing
- Containerized deployment ready

## Recent Changes
- ✅ Successfully migrated from SQLite to PostgreSQL using Neon database
- ✅ Updated database configuration to handle both SQLite and PostgreSQL connections
- ✅ Verified all database tables, relationships, and API endpoints working with PostgreSQL
- ✅ Removed obsolete TypeScript database configuration file
- ✅ Database environment variables configured (DATABASE_URL, PGPORT, PGUSER, etc.)
- ✅ Implemented AI-powered roadmap generator using OpenAI GPT-4 and LangChain
- ✅ Added robust fallback system for roadmap generation when AI API is unavailable
- ✅ Created dedicated roadmap service module with comprehensive error handling
- ✅ Updated roadmap data models to support seconds-based duration and proper structure
- ✅ Added both standalone and project-specific roadmap generation endpoints
- Fixed Python import structure to use absolute imports
- Added email-validator dependency for Pydantic email validation
- Configured all infrastructure files (Docker, nginx, CI/CD)

## API Endpoints
- `/health` - Health check
- `/api/v1/users` - User CRUD operations
- `/api/v1/projects` - Project CRUD operations
- `/api/v1/roadmap/generate` - AI-powered roadmap generation
- `/api/v1/roadmap/health` - Roadmap service health check
- `/api/v1/project/{project_id}/roadmap/generate` - Project-specific roadmap generation
- `/docs` - Interactive API documentation

## Running the Project

### Local Development
```bash
# Backend
cd apps/backend
python main.py

# Frontend
cd apps/frontend
npm install && npm run dev
```

### Docker
```bash
cd infra
docker-compose up -d
```

## User Preferences
*No specific user preferences recorded yet*

## Technical Decisions
- Using absolute imports in Python backend for better module resolution
- PostgreSQL as production database with Neon hosting for scalability and reliability
- Dynamic database configuration supporting both SQLite (fallback) and PostgreSQL
- Monorepo structure for better code organization and sharing
- Docker multi-stage builds for optimized production images
- psycopg2-binary driver for optimal PostgreSQL performance