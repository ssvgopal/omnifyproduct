# Backend Server Startup Guide

## Quick Start

The backend server needs to be running on `http://localhost:8000` for the frontend to work.

## Setting Up Virtual Environment

**Always use a virtual environment for Python projects!**

### Create Virtual Environment

**Windows (Command Prompt)**:
```cmd
cd backend
python -m venv venv
```

**Windows (Git Bash)**:
```bash
cd backend
python -m venv venv
```

### Activate Virtual Environment

**Windows (Command Prompt)**:
```cmd
cd backend
venv\Scripts\activate
```

**Windows (Git Bash)**:
```bash
cd backend
source venv/Scripts/activate
```

You should see `(venv)` in your prompt when activated.

### Install Dependencies

**Windows (Command Prompt)**:
```cmd
pip install -r requirements.txt
```

**Windows (Git Bash)**:
```bash
pip install -r requirements.txt
```

### Deactivate Virtual Environment (when done)

```cmd
deactivate
```

## Starting the Backend Server

**Important**: Make sure your virtual environment is activated first!

### Option 1: Using the Startup Script (Recommended)

**Windows (Command Prompt)**:
```cmd
cd backend
venv\Scripts\activate
python start_server.py
```

**Windows (Git Bash)**:
```bash
cd backend
source venv/Scripts/activate
python start_server.py
```

### Option 2: Direct Python Execution

**Windows (Command Prompt)**:
```cmd
cd backend
venv\Scripts\activate
python agentkit_server.py
```

**Windows (Git Bash)**:
```bash
cd backend
source venv/Scripts/activate
python agentkit_server.py
```

### Option 3: Using Uvicorn Directly

**Windows (Command Prompt)**:
```cmd
cd backend
venv\Scripts\activate
uvicorn agentkit_server:app --host 127.0.0.1 --port 8000 --reload
```

**Windows (Git Bash)**:
```bash
cd backend
source venv/Scripts/activate
uvicorn agentkit_server:app --host 127.0.0.1 --port 8000 --reload
```

## Environment Variables

The server will use default values if environment variables are not set, but you should configure:

### Required for Full Functionality

Create a `.env` file in the `backend` directory:

```env
# MongoDB Connection
MONGO_URL=mongodb://localhost:27017
DB_NAME=omnify_cloud

# JWT Secret (change in production!)
JWT_SECRET_KEY=your-secret-key-here-min-32-chars

# Server Port
PORT=8000

# CORS Origins (for frontend)
CORS_ORIGINS=http://localhost:4000,http://localhost:4001

# Stripe (for paid plans - optional)
STRIPE_SECRET_KEY=sk_test_...

# Email Service (for verification - optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Default Values (if not set)

- `PORT`: 8000
- `MONGO_URL`: mongodb://localhost:27017
- `DB_NAME`: omnify_cloud
- `JWT_SECRET_KEY`: dev-secret-key-change-in-production-12345678901234567890
- `CORS_ORIGINS`: * (allows all origins)

## Prerequisites

### 1. Python Virtual Environment Setup

**Create and activate venv first, then install dependencies:**

**Windows (Command Prompt)**:
```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Windows (Git Bash)**:
```bash
cd backend
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

**Note**: Always activate the virtual environment before running the server or installing packages.

### 2. MongoDB

The backend requires MongoDB. You have two options:

#### Option A: Local MongoDB

1. Install MongoDB locally
2. Start MongoDB service:
   ```cmd
   # Windows - if installed as service, it should start automatically
   # Or start manually:
   mongod --dbpath C:\data\db
   ```

#### Option B: MongoDB Docker Container

**Windows (Command Prompt)**:
```cmd
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

**Windows (Git Bash)**:
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

#### Option C: MongoDB Atlas (Cloud)

Use a MongoDB Atlas connection string:
```env
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/omnify_cloud?retryWrites=true&w=majority
```

## Verifying the Server is Running

Once started, you should see output like:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Test the Server

Open in browser or use curl:
- Health check: `http://localhost:8000/health`
- API info: `http://localhost:8000/api/info`

**Windows (PowerShell)**:
```powershell
Invoke-WebRequest -Uri http://localhost:8000/health
```

**Windows (Git Bash)**:
```bash
curl http://localhost:8000/health
```

## Troubleshooting

### Error: "Connection Refused"

**Problem**: Backend server is not running.

**Solution**: 
1. Start the backend server using one of the methods above
2. Verify it's running on port 8000
3. Check firewall settings if needed

### Error: "Module not found"

**Problem**: Python dependencies not installed.

**Solution**:
```cmd
cd backend
pip install -r requirements.txt
```

### Error: "MongoDB connection failed"

**Problem**: MongoDB is not running or connection string is incorrect.

**Solution**:
1. Verify MongoDB is running:
   ```cmd
   # Check if MongoDB is running
   netstat -an | findstr 27017
   ```
2. Check `MONGO_URL` in `.env` file
3. Start MongoDB if not running

### Error: "Port 8000 already in use"

**Problem**: Another service is using port 8000.

**Solution**:
1. Find what's using the port:
   ```cmd
   netstat -ano | findstr :8000
   ```
2. Kill the process or change the port:
   ```env
   PORT=8001
   ```
   Then update frontend API URL:
   ```env
   REACT_APP_API_URL=http://localhost:8001
   ```

### Error: "CORS policy blocked"

**Problem**: Frontend origin not allowed.

**Solution**:
1. Add frontend URL to `CORS_ORIGINS`:
   ```env
   CORS_ORIGINS=http://localhost:4000,http://localhost:4001
   ```
2. Restart the backend server

## Development vs Production

### Development Mode

- Uses default/weak secrets (OK for local dev)
- Reload on code changes (if using `--reload`)
- Detailed error messages
- CORS allows all origins (if not configured)

### Production Mode

- **MUST** set strong `JWT_SECRET_KEY`
- **MUST** configure proper `CORS_ORIGINS`
- **MUST** use secure MongoDB connection
- **MUST** set up proper logging
- **MUST** use environment variables (not defaults)

## Quick Start Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created (`python -m venv venv`)
- [ ] Virtual environment activated (`venv\Scripts\activate` or `source venv/Scripts/activate`)
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] MongoDB running (local, Docker, or Atlas)
- [ ] `.env` file created in `backend/` directory (optional but recommended)
- [ ] Backend server started (`python start_server.py`)
- [ ] Server accessible at `http://localhost:8000/health`
- [ ] Frontend can connect (no CORS errors)

## Next Steps

Once the backend is running:

1. Test registration: Navigate to `/register` in frontend
2. Check MongoDB: Verify data is being created
3. Test login: Use registered credentials
4. Check logs: Monitor backend console for errors

## Additional Resources

- Backend API Documentation: `http://localhost:8000/docs` (Swagger UI)
- Alternative API Docs: `http://localhost:8000/redoc` (ReDoc)
- Health Check: `http://localhost:8000/health`
- API Info: `http://localhost:8000/api/info`

