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
- User management system with JWT authentication
- Project management
- AI-powered roadmap generation using OpenAI GPT-4 and LangChain
- Intelligent fallback system for robust roadmap generation
- **Advanced roadmap customization features**:
  - Branches library with de-duplicated content
  - Core video identification (essential vs optional content)
  - Custom roadmap creation from existing branches
  - Customization tracking and lineage
  - Duration recalculation and validation
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
- ✅ **Added PostgreSQL roadmaps table for persistent storage**
- ✅ **Implemented complete CRUD operations for roadmap management**
- ✅ **Created SyncRoadmapService for database operations with JSON branch storage**
- ✅ **Integrated database persistence into roadmap generation API**
- ✅ **Added GET /api/v1/roadmap/{user_id} endpoint for user roadmap retrieval**
- ✅ **Added GET/DELETE /api/v1/roadmap/id/{roadmap_id} endpoints for specific roadmap operations**
- ✅ **Tested full end-to-end functionality with database storage and retrieval**
- ✅ **Implemented JWT-based user authentication system**
- ✅ **Created AuthService with bcrypt password hashing and JWT token management**
- ✅ **Added authentication middleware for protecting API endpoints**
- ✅ **Replaced hardcoded "test_user" with real authenticated user IDs**
- ✅ **Secured all roadmap endpoints with Bearer token authentication**
- ✅ **Added user signup, login, and profile management endpoints**
- ✅ **Updated users table with password_hash column for authentication**
- ✅ **ENHANCED ROADMAP CUSTOMIZATION FEATURES** (January 2025)
  - ✅ **Added branches_library to generation response with de-duplicated branches**
  - ✅ **Implemented is_core flag for videos (true=essential, false=optional)**
  - ✅ **Created POST /api/v1/roadmap/customize endpoint for custom roadmaps**
  - ✅ **Added customized_from tracking for roadmap lineage**
  - ✅ **Built branch selection system with duration recalculation**
  - ✅ **Enhanced all data models with customization support**
  - ✅ **Implemented core video protection (prevents removal of essential content)**
  - ✅ **Added comprehensive testing with 100% feature coverage**
- Fixed Python import structure to use absolute imports
- Added email-validator dependency for Pydantic validation
- Added PyJWT and bcrypt dependencies for authentication
- Configured all infrastructure files (Docker, nginx, CI/CD)

## API Endpoints
- `/health` - Health check
- `/api/auth/signup` - User registration with email and password
- `/api/auth/login` - User authentication with JWT token response
- `/api/auth/me` - Get current authenticated user information
- `/api/auth/health` - Authentication service health check
- `/api/v1/users` - User CRUD operations
- `/api/v1/projects` - Project CRUD operations
- `/api/v1/roadmap/generate` - 🔐 **Enhanced AI-powered roadmap generation with branches_library**
- `/api/v1/roadmap/customize` - 🔐 **NEW: Create custom roadmaps from selected branches**
- `/api/v1/roadmap/health` - Roadmap service health check
- `/api/v1/roadmap/my-roadmaps` - 🔐 Get authenticated user's roadmaps (AI-generated + custom)
- `/api/v1/roadmap/id/{roadmap_id}` - 🔐 Get/Delete specific roadmap by ID (user-owned only)
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