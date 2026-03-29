# Deployment & School Demo Guide

## For School Demo

### Pre-Demo Checklist
- [ ] Tested on demo machine
- [ ] Database created with test data
- [ ] Both demo and admin accounts ready
- [ ] Game starting up correctly
- [ ] UI responsive on projector resolution
- [ ] Backend running without errors
- [ ] All payment providers showing in dropdown
- [ ] Admin panel accessible with admin account

### Demo Flow (10-15 minutes)

**1. Show Login (1 min)**
- Open browser on http://localhost:5000
- Show login page with demo credentials
- Explain this is a simulation demo

**2. Account & Dashboard (1 min)**
- Login as demo user
- Show dashboard with balance
- Explain starting balance is $500 demo money

**3. Wallet System (2 min)**
- Go to Wallet tab
- Show deposit options (M-Pesa, MTN, Airtel, etc.)
- Explain these are "simulated for demo"
- Deposit $100
- Show balance updated instantly
- Show transaction in history

**4. Play Game (5 min)**
- Go to Game tab
- Click "START GAME"
- Explain game mechanics:
  - Multiplier starts at 1.00x
  - Increases over time
  - Random crash point (1x to 500x)
- Place a bet ($50)
- Let it run for a few seconds
- Cash out at ~2.0x
- Show winnings calculated: $50 × 2.0 = $100
- Let audience see the win added to balance

**5. Show Game History (1 min)**
- Show previous rounds and crash points
- Explain multiplier distribution

**6. Show Admin Panel (3 min)**
- Logout and login as admin
- Show dashboard with statistics
- Show all users
- Credit/debit demo user balance (show how it works)
- View all transactions
- Show game monitoring
- Explain admin capabilities

**7. Explain Architecture (2 min)**
- Backend: Flask + SQLite (Python)
- Frontend: Vanilla JavaScript, HTML, CSS
- Database: All data persists locally
- Security: JWT authentication, password hashing
- Features: Full-stack web app

---

## Deployment Options

### Option 1: Local Demo (Simplest)
```bash
cd backend
python app.py
# Access at http://localhost:5000
```
✅ Best for: School demo, personal testing

### Option 2: Virtual Machine
- Use VirtualBox or VMware
- Install Python 3.8+
- Follow local setup
- Clone/copy entire project

### Option 3: Cloud Deployment (Production-Ready)

#### Deploy on Heroku
```bash
# Create Heroku app
heroku create aviator-demo

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key

# Deploy
git push heroku main

# Access at https://aviator-demo.herokuapp.com
```

#### Deploy on PythonAnywhere
1. Upload entire project
2. Configure virtualenv
3. Setup WSGI file
4. Point domain to app

#### Deploy on AWS
1. Launch EC2 instance
2. Install Python runtime
3. Use Gunicorn + Nginx
4. Setup RDS for PostgreSQL (optional)

#### Deploy on Google Cloud
1. Create Cloud Run service
2. Push Docker container
3. Or deploy App Engine

### Option 4: Docker Container

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
COPY frontend/ /app/frontend/

EXPOSE 5000

CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t aviator-demo .
docker run -p 5000:5000 aviator-demo
```

---

## Performance Tips

### For Smooth Demo
1. Use modern browser (Chrome/Firefox)
2. Disable browser extensions (they slow down JS)
3. Close other browser tabs
4. Ensure good internet connection (if cloud deployed)
5. Test beforehand on projector

### Backend Optimization
```python
# Enable caching headers
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000

# Use efficient database queries
db.session.query(User).filter_by(id=user_id).first()

# Compress responses
from flask_compress import Compress
Compress(app)
```

### Frontend Optimization
- Minify CSS/JS in production
- Use CDN for assets
- Lazy load images/components
- Reduce animation complexity

---

## Troubleshooting Before Demo

### Test Checklist
```bash
# 1. Start backend
cd backend
python app.py
# Verify: "Running on http://127.0.0.1:5000"

# 2. Test in browser
# Visit: http://localhost:5000
# Verify: Login page loads

# 3. Test demo account
# Login: demo / demo123
# Verify: Dashboard loads with $500 balance

# 4. Test deposits
# Go to Wallet, deposit $100
# Verify: Balance updates to $600

# 5. Test game
# Go to Game, start game
# Place $50 bet
# Cash out at 2x
# Verify: Winnings calculated correctly

# 6. Test admin
# Logout, login as admin/admin123
# Verify: Admin panel accessible
```

### Common Demo Issues & Fixes

**Issue**: Page loading very slow
```
Fix: Close browser tabs, disable extensions, restart Flask
```

**Issue**: Balance not updating
```
Fix: Refresh page, check Network tab in DevTools
```

**Issue**: Can't place bet
```
Fix: Ensure game is started first, check console for errors
```

**Issue**: Game not starting
```
Fix: Check backend is running, verify no errors in terminal
```

**Issue**: Admin panel showing error
```
Fix: Ensure logged in with admin account (admin/admin123)
```

**Issue**: Multiplier stopped updating
```
Fix: Reload game page, may have crashed - click START GAME again
```

---

## Production Checklist

Before deploying to production:

### Security
- [ ] Change SECRET_KEY to random value
- [ ] Enable HTTPS/SSL
- [ ] Setup CSRF protection
- [ ] Validate all inputs
- [ ] Sanitize outputs
- [ ] Rate limit API endpoints
- [ ] Setup firewall rules
- [ ] Enable CORS restriction

### Database
- [ ] Backup strategy in place
- [ ] Database encryption enabled
- [ ] Regular maintenance scheduled
- [ ] Query optimization done
- [ ] Indexes created

### Monitoring
- [ ] Error logging setup (Sentry)
- [ ] Performance monitoring
- [ ] User analytics (if needed)
- [ ] Payment monitoring
- [ ] Uptime monitoring

### Testing
- [ ] Unit tests written
- [ ] Integration tests done
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Payment flow tested

### DevOps
- [ ] CI/CD pipeline setup
- [ ] Automated deployments
- [ ] Rollback procedure ready
- [ ] Documentation complete
- [ ] Team trained

---

## Real Payment Integration for Production

When ready to use real payments:

1. **Get API Credentials**
   - M-Pesa: https://developer.safaricom.co.ke/
   - MTN: Contact MTN Developer
   - Airtel: Contact Airtel
   - Others: Contact provider

2. **Update Code**
   - Remove simulate_payment() calls
   - Implement real API calls
   - Setup webhook handlers
   - Enable signature verification

3. **Configure Environment**
   ```bash
   # Set in production environment
   ENABLE_REAL_PAYMENTS=True
   MPESA_API_KEY=your_real_key
   MPESA_API_SECRET=your_real_secret
   # ... etc for other providers
   ```

4. **Test Thoroughly**
   - Test with real provider sandbox
   - Test all payment scenarios
   - Test error handling
   - Test callback verification
   - Monitor logs

---

## Scaling for Production

If application grows:

### Database Scaling
```python
# Migrate to PostgreSQL
SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@localhost/aviator'

# Add indexes for frequently queried fields
CREATE INDEX idx_user_username ON users(username);
CREATE INDEX idx_bet_user_game ON bets(user_id, game_round_id);
CREATE INDEX idx_transaction_date ON transactions(created_at DESC);
```

### API Scaling
```python
# Use gunicorn with multiple workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Setup load balancer (Nginx)
upstream backend {
    server app1:5000;
    server app2:5000;
    server app3:5000;
}

server {
    listen 80;
    location / {
        proxy_pass http://backend;
    }
}
```

### Frontend Caching
```python
# Add cache headers
@app.after_request
def set_cache_headers(response):
    response.headers['Cache-Control'] = 'public, max-age=3600'
    return response
```

### WebSockets for Real-time
```python
# Current: Polling every 100ms
# Better: WebSocket connection for real-time updates
from flask_socketio import SocketIO, emit

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    emit('response', {'data': 'Connected to game server'})

@socketio.on('subscribe_game')
def subscribe_to_game(data):
    # Subscribe user to game updates
    join_room(f"game_{data['game_id']}")
```

---

## Maintenance

### Regular Tasks
- [ ] Daily: Check error logs
- [ ] Weekly: Backup database
- [ ] Weekly: Review payment logs
- [ ] Monthly: Update dependencies
- [ ] Monthly: Analyze performance
- [ ] Quarterly: Security audit
- [ ] Yearly: Full system review

### Update Dependencies
```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade Flask

# Update all
pip install --upgrade -r requirements.txt

# Save new versions
pip freeze > requirements.txt
```

---

## Demo Night Tips

- Test everything beforehand ✅
- Have backup browser ready
- Show code on projector (use large font)
- Explain "This is a simulation"
- Let audience see the fun parts (playing game, winning bets)
- Show admin panel last (technical details)
- Have demo data ready (don't explain initial setup)
- Speak loudly - not everyone can hear
- Have laptop backup
- Save copy in cloud (USB stick)

---

**Good luck with your presentation! 🚀**
