# Mantrix - Full-Stack Monorepo

A comprehensive full-stack monorepo scaffold with FastAPI backend and React TypeScript frontend, designed for scalable application development.

## 🏗️ Architecture

### Tech Stack
- **Backend**: FastAPI with Python 3.11, SQLAlchemy, Pydantic
- **Frontend**: React 18 with TypeScript, Tailwind CSS, React Query
- **Database**: PostgreSQL (configurable)
- **Infrastructure**: Docker, GitHub Actions CI/CD
- **AI Services**: Resume builder and roadmap generation engines

### Project Structure
```
mantrix/
├── apps/
│   ├── frontend/          # React 18 + TypeScript
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── pages/
│   │   │   ├── lib/
│   │   │   └── ...
│   │   ├── package.json
│   │   └── vite.config.ts
│   └── backend/           # FastAPI + Python 3.11
│       ├── api/           # Route handlers
│       ├── models/        # Pydantic models + DB schemas
│       ├── core/          # Business logic
│       ├── services/      # AI agents, resume builder, roadmap engine
│       ├── tests/         # Unit tests
│       └── main.py
├── infra/                 # Infrastructure as code
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
├── .github/workflows/     # CI/CD pipelines
├── mantrix.env           # Environment variables template
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (for containerized setup)

### Option 1: Local Development

#### Backend Setup
```bash
cd apps/backend

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp ../../mantrix.env .env
# Edit .env with your configuration

# Run database migrations (if using PostgreSQL)
alembic upgrade head

# Start the server
python main.py
```

#### Frontend Setup
```bash
cd apps/frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

### Option 2: Docker Setup

```bash
# Clone the repository
git clone <repository-url>
cd mantrix

# Copy environment file
cp mantrix.env .env
# Edit .env with your configuration

# Start all services
cd infra
docker-compose up -d

# View logs
docker-compose logs -f
```

## 🌐 API Documentation

Once the backend is running, visit:
- API Documentation: `http://localhost:8000/docs`
- Alternative API Docs: `http://localhost:8000/redoc`

## 🔧 Development

### Backend Development

#### Available Scripts
```bash
# Run tests
pytest tests/ -v

# Code formatting
black .
isort .

# Linting
flake8 .

# Type checking
mypy .
```

#### Adding New Routes
1. Create route handlers in `apps/backend/api/routes.py`
2. Add Pydantic models in `apps/backend/models/schemas.py`
3. Implement business logic in `apps/backend/services/`
4. Add tests in `apps/backend/tests/`

### Frontend Development

#### Available Scripts
```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Linting
npm run lint

# Type checking
npm run type-check
```

#### Adding New Pages
1. Create component in `apps/frontend/src/pages/`
2. Add route in `apps/frontend/src/App.tsx`
3. Update navigation in `apps/frontend/src/components/Layout.tsx`

## 🧪 Testing

### Backend Tests
```bash
cd apps/backend
pytest tests/ -v --cov=.
```

### Frontend Tests
```bash
cd apps/frontend
npm test
```

### Integration Tests
```bash
# Using Docker Compose
docker-compose -f infra/docker-compose.yml -f infra/docker-compose.test.yml up --abort-on-container-exit
```

## 🚢 Deployment

### Using Docker
```bash
# Build images
docker-compose -f infra/docker-compose.yml build

# Deploy to production
docker-compose -f infra/docker-compose.yml -f infra/docker-compose.prod.yml up -d
```

### Environment Variables

Key environment variables to configure:

```bash
# App Configuration
APP_NAME=Mantrix
DEBUG=false
VERSION=1.0.0

# Database
DATABASE_URL=postgresql://username:password@localhost/mantrix

# Security
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256

# AI Services
OPENAI_API_KEY=your-openai-api-key

# External Services
SENDGRID_API_KEY=your-sendgrid-key
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
```

## 🤖 AI Features

### Resume Builder
- Generate professional resumes using AI
- Extract skills from user projects
- Multiple template styles
- PDF export functionality

### Roadmap Engine
- Create personalized learning roadmaps
- Skill level assessment
- Time-based milestone planning
- Resource recommendations

## 📚 API Endpoints

### Users
- `GET /api/v1/users` - Get all users
- `POST /api/v1/users` - Create user
- `GET /api/v1/users/{id}` - Get user by ID
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

### Projects
- `GET /api/v1/projects` - Get all projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects/{id}` - Get project by ID
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

### AI Services
- `POST /api/v1/resume/generate` - Generate resume
- `POST /api/v1/roadmap/generate` - Generate roadmap

## 🔒 Security

- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy
- CORS configuration
- Security headers in Nginx
- Environment variable management
- Dependency vulnerability scanning

## 📊 Monitoring

- Health check endpoints
- Docker health checks
- Application logging
- Error tracking (configurable with Sentry)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Create an issue for bug reports or feature requests
- Check the documentation in `/docs` folder
- Review API documentation at `http://localhost:8000/docs`

## 🗺️ Roadmap

- [ ] Authentication & authorization
- [ ] Real-time features with WebSockets
- [ ] File upload and storage
- [ ] Advanced AI integrations
- [ ] Mobile application
- [ ] Microservices architecture
- [ ] Kubernetes deployment