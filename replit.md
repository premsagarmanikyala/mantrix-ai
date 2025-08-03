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
- **Flexible resume builder with progress tracker integration**:
  - Study Mode: Resume based on completed modules only
  - Fast Mode: Full roadmap content resume generation
  - Analyzer Mode: Resume vs job description analysis with ATS scoring
  - Progress tracking and module completion monitoring
  - AI-powered content generation and skills analysis
- **AI-powered learning path recommendation system**:
  - Gap Analysis: Skills needed for target job roles
  - Resume Enhancement: Profile improvement suggestions
  - Interest-Based: Personalized paths from user preferences
  - User progress integration and skill profiling
  - Confidence scoring and actionable next steps
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
- ✅ **RESUME BUILDER WITH PROGRESS TRACKER INTEGRATION** (August 2025)
  - ✅ **Implemented three resume generation modes (study, fast, analyzer)**
  - ✅ **Built progress tracking system for module completion**
  - ✅ **Created AI-powered resume generation with OpenAI GPT-4 integration**
  - ✅ **Added ATS-compatible resume analysis and scoring**
  - ✅ **Implemented job description vs resume matching**
  - ✅ **Built database persistence for resumes and progress data**
  - ✅ **Integrated JWT authentication for secure user data management**
  - ✅ **Added comprehensive error handling and fallback systems**
  - ✅ **Created multi-mode resume storage and retrieval**
- ✅ **DEDICATED PROGRESS TRACKER + SUMMARY API** (August 2025)
  - ✅ **Implemented POST /api/v1/progress/complete for module completion tracking**
  - ✅ **Built GET /api/v1/progress/summary for comprehensive analytics**
  - ✅ **Added PostgreSQL persistence with duplicate prevention**
  - ✅ **Created JWT-authenticated user ownership validation**
  - ✅ **Implemented frontend-friendly data format for visualizations**
  - ✅ **Built branch-level progress breakdowns and analytics**
  - ✅ **Added duration tracking and percentage calculations**
  - ✅ **Created real-time progress updates and summaries**
- ✅ **AI-POWERED LEARNING PATH RECOMMENDATION SYSTEM** (August 2025)
  - ✅ **Implemented POST /api/v1/roadmap/recommend with multi-mode analysis**
  - ✅ **Built Gap Analysis mode for job description skills matching**
  - ✅ **Created Resume Enhancement mode for profile improvement**
  - ✅ **Added Interest-Based mode for personalized learning paths**
  - ✅ **Integrated OpenAI GPT-4 for intelligent recommendation generation**
  - ✅ **Built comprehensive user progress integration and skill profiling**
  - ✅ **Added fallback system for reliable recommendations without AI**
  - ✅ **Implemented confidence scoring and actionable next steps**
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
- `/api/v1/roadmap/customize` - 🔐 **Create custom roadmaps from selected branches**
- `/api/v1/roadmap/health` - Roadmap service health check
- `/api/v1/roadmap/my-roadmaps` - 🔐 Get authenticated user's roadmaps (AI-generated + custom)
- `/api/v1/roadmap/id/{roadmap_id}` - 🔐 Get/Delete specific roadmap by ID (user-owned only)
- `/api/v1/project/{project_id}/roadmap/generate` - Project-specific roadmap generation
- `/api/v1/resume/generate` - 🔐 **Multi-mode resume generation (study/fast/analyzer)**
- `/api/v1/resume/my-resumes` - 🔐 **Get user's saved resumes with statistics**
- `/api/v1/resume/progress/complete` - 🔐 **Mark learning modules as completed**
- `/api/v1/resume/progress` - 🔐 **Get user's learning progress statistics**
- `/api/v1/resume/health` - Resume service health check
- `/api/v1/progress/complete` - 🔐 **NEW: Dedicated module completion tracking with duration**
- `/api/v1/progress/summary` - 🔐 **NEW: Comprehensive progress analytics with branch breakdowns**
- `/api/v1/progress/health` - Progress service health check
- `/api/v1/roadmap/recommend` - 🔐 **NEW: AI-powered learning path recommendations (gap/resume/interest modes)**
- `/api/v1/roadmap/recommend/health` - Recommendation service health check
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