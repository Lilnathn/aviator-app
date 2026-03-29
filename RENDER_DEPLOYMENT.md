# 🚀 Render Deployment Guide

Complete step-by-step guide to deploy the Aviator application on Render.

---

## Prerequisites

- GitHub account (for connecting your repository)
- Render account (free at https://render.com)
- Git installed locally
- Project pushed to GitHub

---

## Step 1: Verify Project Files

Make sure you have these key files in your project root:

```
✅ Procfile                  (gunicorn start command)
✅ .env.example              (environment variables template)
✅ requirements.txt          (in backend/ folder)
✅ README.md                 (documentation)
✅ backend/app.py            (Flask application)
```

Verify Procfile exists:
```bash
cat Procfile
# Should output: web: cd backend && gunicorn app:app
```

---

## Step 2: Prepare GitHub Repository

### 2.1 Commit and Push All Changes

```bash
# Navigate to project directory
cd /path/to/aviator-app

# Stage all files
git add .

# Commit
git commit -m "Prepare for Render deployment"

# Push to main branch
git push origin main
```

### 2.2 Verify on GitHub

Visit https://github.com/YOUR_USERNAME/aviator-app and verify:
- ✅ All files are present
- ✅ Procfile is there
- ✅ backend/requirements.txt exists
- ✅ Latest commit shows your changes

---

## Step 3: Create Render Account

1. Go to https://render.com
2. Click **"Sign Up"**
3. Connect with GitHub (recommended)
4. Authorize Render to access your repositories

---

## Step 4: Create Web Service on Render

### 4.1 Create New Service

1. In Render dashboard, click **"New +"**
2. Select **"Web Service"**

### 4.2 Connect Repository

1. Click **"Connect your GitHub account"** (if not already connected)
2. Select your repository: **aviator-app**
3. Click **"Connect"**

### 4.3 Configure Service

Fill in the following:

```
Name:                   aviator-app
Environment:            Python 3
Build Command:          pip install -r backend/requirements.txt
Start Command:          cd backend && gunicorn app:app
Plan:                   Free (sufficient for demo)
Region:                 Choose closest to you
```

### 4.4 Set Environment Variables

**CRITICAL:** Set these before deploying!

1. Scroll to **"Environment"** section
2. Click **"Add Environment Variable"**
3. Add these variables:

| Key | Value | Notes |
|-----|-------|-------|
| `FLASK_ENV` | `production` | Required |
| `SECRET_KEY` | Generate a random string | Use strong key! |
| `JWT_SECRET` | Same as SECRET_KEY or unique | JWT signing key |

**To generate a strong SECRET_KEY:**

```bash
# On your computer, run:
python -c "import secrets; print(secrets.token_hex(32))"
# Copy the output and paste into SECRET_KEY
```

**Example values:**
```
SECRET_KEY = 2f8b3d4c9e2a1f7b6c9d4e2a1f7b6c9d
JWT_SECRET = 2f8b3d4c9e2a1f7b6c9d4e2a1f7b6c9d
```

### 4.5 Review and Deploy

1. Verify all settings are correct
2. Click **"Create Web Service"**
3. Render will start building (2-3 minutes)

---

## Step 5: Verify Deployment

### 5.1 Wait for Build

In Render dashboard:
- **Build** phase: Installing dependencies (1-2 min)
- **Deploy** phase: Starting app (30-60 sec)
- **Live**: Green checkmark means success!

### 5.2 Check Logs

Click **"Logs"** in Render dashboard. Should see:

```
=== Checking for gunicorn
=== Building...
...
Starting gunicorn
Listening on 0.0.0.0:10000
```

If there are errors, see **Troubleshooting** section below.

### 5.3 Test the Deployment

Get your app URL from Render dashboard (Format: `https://your-app-name.onrender.com`)

Test endpoints:

```bash
# Test root (backend health)
curl https://your-app-name.onrender.com/

# Should return:
# {
#   "status": "success",
#   "message": "Aviator Backend is Running",
#   "mode": "🎓 DEMO MODE - School Project, Simulation Only",
#   "demo_credentials": {...}
# }
```

---

## Step 6: Access the Application

### Frontend
```
https://your-app-name.onrender.com/app
```

### Credentials
```
Username: demo
Password: demo123
Balance: $500

OR

Username: admin
Password: admin123
Balance: $10,000
```

---

## Step 7: Update Frontend Configuration (If Needed)

If frontend can't connect to backend, update `frontend/index.html`:

Find this section:
```html
<!--
    ============================================================================
    Configuration for API Backend
    ...
-->
```

Uncomment and update:
```html
<script>
    window.CONFIG = {
        API_BASE_URL: 'https://your-app-name.onrender.com/api',
        environment: 'render'
    };
</script>
```

Then in Render dashboard:
1. Click your service
2. Click **"Redeploy"**
3. Wait for new build to complete

---

## Troubleshooting

### Build Fails: "ModuleNotFoundError"

**Problem:** Module not found when building

**Solution:**
1. Check `backend/requirements.txt` has all imports
2. Example: if you import `flask_cors`, ensure `Flask-CORS` is in requirements.txt
3. Verify versions match local setup
4. Fix locally first, commit, and redeploy

### Build Fails: "gunicorn: command not found"

**Problem:** Gunicorn not installed

**Solution:**
```bash
# Ensure this is in backend/requirements.txt:
gunicorn==21.2.0

# Add if missing, commit, and redeploy:
git add backend/requirements.txt
git commit -m "Add gunicorn to requirements"
git push origin main
```

### App Builds but Won't Start

**Problem:** Build succeeds but app won't start

**Check logs for errors.**

Common issues:
- Database error: DATABASE_URL not set (if using PostgreSQL)
- Environment variable missing: Set in Render dashboard
- Port issue: Render sets PORT automatically, don't hardcode it

### Connection Refused: Can't Connect to Backend

**Problem:** Frontend can't reach backend API

**Solutions:**
1. Verify app is running (check logs in Render)
2. Check frontend is accessing correct URL:
   ```javascript
   // Open browser console and check:
   console.log(API_BASE_URL);
   // Should print: https://your-app.onrender.com/api
   ```
3. If URLs don't match, update in `frontend/index.html`
4. Check CORS settings in `backend/app.py` (should be enabled)

### "Invalid or expired token"

**Problem:** Login works but then unauthorized

**Cause:** SECRET_KEY changed or JWT_SECRET not set

**Solution:**
1. Ensure JWT_SECRET is set in Render environment
2. Make sure it matches or is set correctly
3. May need to re-login after fix

### Free Tier Spins Down

**Problem:** App goes to sleep after 15 min inactivity

**Expected behavior:** Free tier services spin down after inactivity. When you visit:
- First visit: ~30 sec to wake up
- Subsequent visits: Fast

**Solution:** Use Render's paid tier ($7-$10/month) to keep running continuously.

---

## Free Tier vs Paid Tier Comparison

| Feature | Free | Paid |
|---------|------|------|
| Cost | $0 | $7+/month |
| Spins down | Yes (15 min) | No |
| Storage | 0.5 GB | Configurable |
| RAM | Shared | Dedicated |
| For demo | ✅ Perfect | Overkill |
| For production | ❌ Not recommended | ✅ Recommended |

---

## Redeploy After Code Changes

Every time you push to GitHub, Render automatically redeploys:

```bash
# Make changes locally
# Test locally (python app.py)
git add .
git commit -m "Description of changes"
git push origin main

# Render automatically:
# 1. Pulls new code from GitHub
# 2. Runs build command
# 3. Starts new instance
# Watch logs in Render dashboard!
```

---

## Demo Presentation Tips

### Before Presenting

1. ✅ Test login with demo credentials
2. ✅ Place a test bet
3. ✅ Show admin panel
4. ✅ Test API with curl/Postman
5. ✅ Check on projector resolution
6. ✅ Have backup (local running version)

### During Presentation

1. **Show Backend Health** (1 min)
   ```
   Visit: https://your-app.onrender.com/
   Show: DEMO MODE banner, credentials
   ```

2. **Login & Play** (3 min)
   - Username: demo, Password: demo123
   - Show dashboard
   - Place bet, show multiplier
   - Continue to demo win

3. **Show Admin Features** (2 min)
   - Login as admin
   - Show users list, transactions
   - Explain database relationships
   - Show data export

4. **Q&A** (5 min)

---

## Additional Resources

- Render Documentation: https://render.com/docs
- Python on Render: https://render.com/docs/deploy-python
- Flask Deployment: https://flask.palletsprojects.com/deployment/
- PostgreSQL on Render: https://render.com/docs/databases

---

## Support & Help

### Common Issues

1. Review logs in Render dashboard
2. Check all environment variables are set
3. Verify requirements.txt is complete
4. Test locally first: `cd backend && python app.py`
5. Ensure Procfile is correct

### Quick Checklist

- [ ] Procfile exists in project root
- [ ] requirements.txt in backend/ has gunicorn
- [ ] All environment variables set in Render
- [ ] Python 3 environment selected
- [ ] Build command: `pip install -r backend/requirements.txt`
- [ ] Start command: `cd backend && gunicorn app:app`
- [ ] Database (if using PostgreSQL) attached
- [ ] App accessible at `https://your-app.onrender.com/`

---

**Status:** ✅ Ready for Deployment

Last Updated: March 2026
