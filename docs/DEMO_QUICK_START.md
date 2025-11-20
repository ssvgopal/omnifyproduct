# 🚀 Demo Quick Start Guide

## Overview
This guide helps you quickly set up and run the demo for OmniFy Cloud Connect.

---

## ✅ What's Ready for Demo

### **1. Integration Setup** ⭐ **PRIMARY FEATURE**
- Google Ads OAuth2 connection
- Meta Ads OAuth2 connection
- Connection status management
- Token refresh/disconnect

### **2. Dashboard Overview**
- Key metrics display
- Quick actions
- Recent activity feed

### **3. Campaign Management**
- Campaign listing
- Campaign creation
- Performance metrics

### **4. Analytics Dashboard**
- Performance charts
- Cross-platform analytics

---

## 🏃 Quick Start

### **1. Start Backend**
```bash
cd backend
python -m uvicorn agentkit_server:app --reload --port 8000
```

### **2. Start Frontend**
```bash
cd frontend
npm install  # If first time
npm start
```

### **3. Access Demo**
- Open browser: `http://localhost:3000/demo`
- Or navigate to: `http://localhost:3000` → Click "Demo"

---

## 📋 Demo Flow

### **5-Minute Quick Demo**

1. **Overview** (30s)
   - Show dashboard with key metrics
   - Highlight recent activity

2. **Integration Setup** (2 min)
   - Go to "Integrations" tab
   - Click "Connect Google Ads"
   - Show OAuth2 popup flow
   - Show connection status update
   - Repeat for Meta Ads

3. **Campaign Management** (2 min)
   - Go to "Campaigns" tab
   - Show existing campaigns
   - Create a new campaign
   - View performance metrics

4. **Analytics** (30s)
   - Go to "Analytics" tab
   - Show performance charts
   - Highlight cross-platform insights

---

## 🔧 Configuration

### **Environment Variables (Backend)**

Create `.env` file in `backend/`:

```bash
# OAuth2 Credentials (for demo, can use test values)
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_REDIRECT_URI=http://localhost:3000/integrations/google-ads/callback

META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
META_REDIRECT_URI=http://localhost:3000/integrations/meta-ads/callback

# Database
MONGODB_URL=mongodb://localhost:27017
DB_NAME=omnify

# Encryption
ENCRYPTION_KEY=your_32_byte_key_here
JWT_SECRET=your_jwt_secret_here
```

### **Frontend Configuration**

Create `.env` file in `frontend/`:

```bash
REACT_APP_BACKEND_URL=http://localhost:8000
```

---

## 🎯 Key Demo Points

### **What to Highlight**:
1. ✅ **OAuth2 Security**: Industry-standard authentication
2. ✅ **Multi-Platform**: Unified interface for Google Ads and Meta Ads
3. ✅ **Real-Time Data**: Live performance metrics
4. ✅ **Easy Setup**: Simple integration process
5. ✅ **Professional UI**: Modern, responsive design

### **What to Acknowledge**:
- Some features use mock data (will connect to real APIs)
- MFA, RBAC UIs are in development
- Advanced features coming in next phase

---

## 🐛 Troubleshooting

### **Backend won't start**
- Check if port 8000 is available
- Verify MongoDB is running
- Check environment variables

### **Frontend won't connect**
- Verify backend is running on port 8000
- Check `REACT_APP_BACKEND_URL` in frontend `.env`
- Check browser console for errors

### **OAuth2 not working**
- Verify OAuth2 credentials are set
- Check redirect URIs match
- Ensure OAuth2 app is configured correctly

---

## 📝 Notes

- **Mock Data**: Some components use mock data for demo
- **API Endpoints**: All backend APIs are ready
- **OAuth2**: Requires proper credentials
- **Error Handling**: Components include error handling

---

**Last Updated**: January 2025

