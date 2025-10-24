# Omnify Cloud Connect - Replit Setup

## Project Overview

**Omnify Cloud Connect** is an AI-powered marketing automation platform with the following architecture:
- **Backend**: Python FastAPI server (Port 8000)
- **Frontend**: React application with Material UI and shadcn/ui components (Port 5000)
- **Database**: MongoDB (requires external setup)
- **Key Features**: AgentKit integration, multi-platform marketing automation, predictive intelligence

## Current Setup Status

### ✅ Completed
- Python 3.11 and Node.js 20 installed
- Backend Python dependencies installed (FastAPI, uvicorn, motor, pydantic, etc.)
- Frontend Node.js dependencies installed (React 19, radix-ui components, etc.)
- Backend workflow configured and running on port 8000
- Frontend workflow configured and running on port 5000
- CORS configured for cross-origin requests
- Frontend configured to proxy `/api` requests to backend

### ⚠️ Pending Configuration
- **MongoDB Connection**: The application requires a MongoDB database
  - Set the `MONGO_URL` environment variable to your MongoDB connection string
  - Example: `mongodb+srv://username:password@cluster.mongodb.net/omnify_cloud`
  - You can use MongoDB Atlas free tier (M0) for development
  
- **API Keys** (Optional for full functionality):
  - `OPENAI_API_KEY` - For AI features and AgentKit fallback
  - `AGENTKIT_API_KEY` - For AgentKit integration
  - Various platform integration keys (Google Ads, Meta Ads, etc.)

## Project Structure

```
.
├── backend/
│   ├── api/                  # API routes
│   ├── core/                 # Core authentication and gateway logic
│   ├── services/             # Business logic services
│   ├── models/               # Pydantic models
│   ├── integrations/         # Platform integrations (Google Ads, Meta, etc.)
│   ├── agentkit_server.py    # Main server (with full features)
│   └── simple_server.py      # Simplified health check server (currently running)
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API client services
│   │   └── hooks/            # Custom React hooks
│   └── public/               # Static assets
└── docs/                     # Comprehensive documentation

```

## Running the Application

### Development Mode (Current)
Both workflows are configured and running automatically:
1. **Backend Server** - Runs on http://localhost:8000
2. **Frontend** - Runs on https://[replit-url]:5000 (visible to user)

### Testing the Backend
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "Backend server is operational"
}
```

## Next Steps for Full Functionality

1. **Set up MongoDB**:
   - Create a MongoDB Atlas account (free tier available)
   - Create a cluster and get the connection string
   - Add `MONGO_URL` to Replit Secrets

2. **Initialize Database Schema**:
   ```bash
   cd backend && python database/mongodb_schema.py
   ```

3. **Switch to Full Server** (after MongoDB is configured):
   - Update Backend Server workflow command to: `cd backend && python agentkit_server.py`
   - This enables all features including AgentKit integration

4. **Add API Keys** (optional):
   - Use Replit Secrets to add API keys for integrations
   - See `env.example` for complete list of supported integrations

## Known Issues

### Frontend Build Warnings
- React 19 peer dependency conflicts with some libraries (react-day-picker, etc.)
- Resolved by using `--legacy-peer-deps` flag
- Does not affect functionality

### Backend Import Errors (Full Server)
- Some services require additional dependencies
- Simple health check server is running instead
- Full functionality requires MongoDB connection

## Documentation

Comprehensive documentation is available in the `/docs` directory:
- `QUICK_START.md` - Quick start guide
- `ARCHITECTURE_DIAGRAMS.md` - System architecture
- `API_USAGE_GUIDE.md` - API documentation
- `DEPLOYMENT_GUIDE.md` - Production deployment guide

## Recent Changes (Replit Import Setup)

- Created `backend/simple_server.py` for quick health check without MongoDB
- Configured `frontend/craco.config.js` to allow all hosts for Replit proxy
- Set up two workflows: Backend Server (port 8000) and Frontend (port 5000)
- Installed all required dependencies via Replit packager

## Support & Resources

- Original README: `/README.md`
- Implementation roadmap: `/implementation_roadmap_10Oct.md`
- Feature documentation: `/docs` directory
