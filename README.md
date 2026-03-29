# 🎮 Aviator Betting Application

A **school project demonstration** of an Aviator-style betting game built with Flask, SQLAlchemy, and vanilla JavaScript. This is a **simulation only** - no real gambling or real money involved.

**Live Demo:** The application is designed to be deployed on [Render](https://render.com) for easy school presentation.

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Demo Credentials](#demo-credentials)
- [Local Development](#local-development)
- [Render Deployment](#render-deployment)
- [API Endpoints](#api-endpoints)
- [Demo Mode Features](#demo-mode-features)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

### Core Features
✅ **User Authentication** - JWT-based login with secure passwords  
✅ **Wallet System** - Deposit, withdraw, transaction history  
✅ **Aviator Game** - Real-time multiplier, crash detection, betting  
✅ **Game Simulation** - Realistic crash distributions (not rigged)  
✅ **Admin Dashboard** - User management, transaction monitoring, data export  
✅ **Payment API Structure** - Ready for M-Pesa, MTN, Airtel integration  
✅ **Responsive UI** - Dark theme, works on mobile/tablet/desktop  

### Demo Mode (School-Friendly)
🎓 **Two Demo Users** - `demo` / `demo123` (500 USD), `admin` / `admin123` (10,000 USD)  
🎓 **Demo Routes** - Force win/lose, control multiplier for presentation  
🎓 **No Real Money** - 100% simulation, all transactions are fake  
🎓 **Quick Testing** - Visit `/` to see backend health and credentials  

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Flask 2.3.2, SQLAlchemy 2.0 |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript (ES6+) |
| **Database** | SQLite (dev) / PostgreSQL (Render) |
| **Auth** | JWT (PyJWT 2.8.0) |
| **Server** | Gunicorn 21.2.0 |
| **Deployment** | Render (https://render.com) |

---

## 🔐 Demo Credentials

**Admin Account (Full Access)**
```
Username: admin
Password: admin123
Initial Balance: $10,000 USD
```

**Demo User Account (Regular User)**
```
Username: demo
Password: demo123
Initial Balance: $500 USD
```

**Test User Account**
```
Username: testuser
Password: testuser123
Initial Balance: $1,000 USD
```

These accounts are **created automatically** on first run.

---

## 🚀 Local Development

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git (for version control)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Lilnathn/aviator-app.git
   cd aviator-app
   ```

2. **Navigate to backend**
   ```bash
   cd backend
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open in browser**
   ```
   Backend API: http://localhost:5000
   Frontend: http://localhost:5000/app
   ```

6. **Login**
   - Use credentials above (admin/admin123 or demo/demo123)
   - Backend health check: `http://localhost:5000/`

### Quick Test
```bash
# Test backend is running
curl http://localhost:5000/

# Check API health
curl http://localhost:5000/api/health
```

---

## 🌍 Render Deployment

### Deploy in 5 Minutes

#### Step 1: Prepare for Deployment

```bash
# From project root, ensure Procfile exists
cat Procfile
# Output: web: cd backend && gunicorn app:app
```

#### Step 2: Push to GitHub

```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

#### Step 3: Create Render Service

1. Go to [https://render.com](https://render.com)
2. Sign up or log in
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub repository
5. Configure:
   - **Name:** `aviator-app` (or your preference)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `cd backend && gunicorn app:app`
   - **Plan:** Free tier works for demo

#### Step 4: Set Environment Variables

In Render dashboard, go to **Environment**:

```
FLASK_ENV=production
SECRET_KEY=generate-a-strong-key-here
JWT_SECRET=same-as-secret-key
```

**Optional (if using PostgreSQL):**
- If you add a PostgreSQL database on Render, it provides `DATABASE_URL` automatically

#### Step 5: Deploy

- Render automatically deploys every `git push`
- Wait for build to complete (~2-3 minutes)
- Your app will be at: `https://your-app.onrender.com`

### Verify Deployment

```bash
# Test the deployment
curl https://your-app.onrender.com/

# Check API health
curl https://your-app.onrender.com/api/health

# Login (get token)
curl -X POST https://your-app.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}'
```

---

## 📡 API Endpoints

### Authentication
```
POST   /api/auth/register      Register new user
POST   /api/auth/login         Login, get JWT token
GET    /api/auth/verify        Verify token
```

### Wallet
```
GET    /api/wallet/balance     Get user balance
POST   /api/wallet/deposit     Deposit funds (simulated)
POST   /api/wallet/withdraw    Withdraw funds
GET    /api/wallet/transactions List transactions (paginated)
```

### Game
```
POST   /api/game/start         Start new game round
GET    /api/game/state         Get current game state
POST   /api/game/bet           Place bet on current game
POST   /api/game/cashout       Cash out from bet
GET    /api/game/history       Get recent game rounds
POST   /api/game/update-multiplier Update multiplier (polling)
```

### Admin
```
GET    /api/admin/dashboard    Dashboard stats
GET    /api/admin/users        List all users
POST   /api/admin/users/{id}/credit   Credit user (admin)
GET    /api/admin/transactions List transactions
GET    /api/admin/export/users Export users as JSON
GET    /api/admin/export/transactions Export transactions as JSON
```

### Health
```
GET    /                       Backend health + demo info
GET    /api/health             API health check
```

---

## 🎓 Demo Mode Features

### For School Presentations

#### 1. **Frontend Configuration**
To switch from localhost to Render in the browser console:

```javascript
// Option A: Native auto-detection
// The app automatically detects if you're on localhost vs deployed
// Just refresh and it works!

// Option B: Manual configuration (not needed usually)
window.CONFIG = {
  API_BASE_URL: 'https://your-app.onrender.com/api'
};
// Then reload the page
```

#### 2. **Admin Demo Routes** (For controlling game during presentation)

Login as **admin** to access demo routes:

```bash
# Force game to crash
curl -X POST https://your-app.onrender.com/api/game/demo/force-crash \
  -H "Authorization: Bearer $TOKEN"

# Force a bet to win with 2.5x multiplier
curl -X POST https://your-app.onrender.com/api/game/demo/force-win/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"multiplier": 2.5}'

# Force a bet to lose
curl -X POST https://your-app.onrender.com/api/game/demo/force-lose/1 \
  -H "Authorization: Bearer $TOKEN"

# Manually set multiplier (demo)
curl -X POST https://your-app.onrender.com/api/game/demo/set-multiplier/5.25 \
  -H "Authorization: Bearer $TOKEN"
```

#### 3. **Suggested Demo Flow** (10-15 minutes)

1. **Show Backend Health** (1 min)
   - Visit `https://your-app.onrender.com/` in browser
   - Show DEMO MODE banner and running status

2. **Demo Login** (1 min)
   - Login with `demo` / `demo123`
   - Show Dashboard with balance

3. **Game Play** (3 min)
   - Go to Game page
   - Place a small bet ($10)
   - If using admin, force a win with 2.5x multiplier
   - Show winnings cashed out

4. **Admin Panel** (3 min)
   - Login as `admin` / `admin123`
   - Show Users list, Transactions, Games
   - Show data export feature
   - Explain payment integration structure

5. **Database** (2 min)
   - Show SQLite/PostgreSQL structure
   - Explain User → Transaction → Bet relationships

6. **Q&A** (5 min)

---

## 🐛 Troubleshooting

### "Cannot connect to backend"

**Local Development:**
```bash
# Make sure you're in the backend directory
cd backend

# Kill any process on port 5000
# Windows: netstat -ano | findstr :5000
# Mac/Linux: lsof -i :5000

# Try running again
python app.py
```

**Render Deployment:**
```bash
# Check logs in Render dashboard
# Click your service → "Logs"

# Common issues:
# - Dependencies not installed: check requirements.txt syntax
# - PORT not set: Render sets PORT env var automatically
# - DATABASE_URL: If using PostgreSQL, ensure DB is created
```

### "401 Unauthorized" when calling API
- Ensure token is in `Authorization: Bearer $TOKEN` header
- Token expires after 24 hours (set in JWT_EXPIRATION_HOURS)
- Admin routes require `is_admin=True` on user account

### Database errors on Render
- If using PostgreSQL, create a PostgreSQL database service in Render dashboard
- The DATABASE_URL is provided automatically
- First deploy might fail - try redeploying the service

### Frontend not loading
- Make sure you're visiting `https://your-app.onrender.com/app`
- Not `/` (which shows backend health info)
- Check browser console for errors
- Check Render logs for backend issues

### "gunicorn: command not found"
- Ensure `gunicorn==21.2.0` is in `backend/requirements.txt`
- Check Python dependencies installed: `pip list | grep gunicorn`

---

## 📁 Project Structure

```
aviator-app/
├── backend/
│   ├── app.py                 # Flask application factory
│   ├── requirements.txt       # Python dependencies
│   ├── models/
│   │   └── database.py        # SQLAlchemy models (5 tables)
│   ├── services/
│   │   ├── auth_service.py    # JWT authentication
│   │   ├── wallet_service.py  # Wallet & transactions
│   │   ├── game_service.py    # Game logic & simulation
│   │   └── payment_service.py # Payment provider integration
│   └── routes/
│       ├── auth_routes.py     # Auth endpoints
│       ├── wallet_routes.py   # Wallet endpoints
│       ├── game_routes.py     # Game endpoints (+ demo routes)
│       └── admin_routes.py    # Admin endpoints
│
├── frontend/
│   ├── index.html             # Single-page app entry point
│   └── assets/
│       ├── css/
│       │   ├── style.css      # Main UI styles
│       │   ├── game.css       # Game interface
│       │   └── admin.css      # Admin panel
│       └── js/
│           ├── api.js         # API client (auto-detects localhost vs Render)
│           ├── game.js        # Game engine
│           ├── ui.js          # UI utilities
│           └── app.js         # Main application
│
├── Procfile                   # Render deployment config
├── .env.example               # Environment variables template
└── README.md                  # This file
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` with your values. Key variables:

```
FLASK_ENV=production              # production or development
SECRET_KEY=your-strong-secret     # Generate a random key
JWT_SECRET=your-jwt-secret        # JWT signing key
DATABASE_URL=                     # Set by Render for PostgreSQL
```

---

## 📚 Documentation Files

- **README.md** - This file (setup, deployment, API reference)
- **QUICKSTART.md** - 5-minute quick start guide
- **DEPLOYMENT.md** - Detailed deployment & demo guide
- **PAYMENT_INTEGRATION.md** - Real payment provider setup
- **FILE_STRUCTURE.md** - Complete file inventory & schema
- **.env.example** - Environment configuration template

---

## 📝 License

This project is created for **educational purposes only** as a school demonstration project. It is not intended for real gambling or commercial use.

---

## 🤝 Contributing

To improve this project:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📧 Support

For issues or questions:
- Check **Troubleshooting** section above
- Review **Render logs** for deployment issues
- Check browser **Console** for frontend errors
- Refer to **DEPLOYMENT.md** for detailed guidance

---

## 🎓 School Presentation Checklist

Before presenting to your class:

- [ ] Deploy to Render (or run locally)
- [ ] Test login with demo credentials
- [ ] Test placing a bet and cashing out
- [ ] Show admin panel features
- [ ] Test `/` route to show health status
- [ ] Demonstrate database structure
- [ ] Have API endpoint examples ready
- [ ] Practice the 10-15 min demo flow
- [ ] Test on projector resolution
- [ ] Have backup (local running version)

---

**Last Updated:** March 2026  
**Status:** ✅ Ready for Deployment & Presentation

