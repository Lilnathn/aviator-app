# QUICK START GUIDE
## Get Running in 5 Minutes

### Prerequisites
- Python 3.8+
- Any modern web browser

### Step 1: Install Dependencies (1 min)
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Start Backend (30 seconds)
```bash
python app.py
```
✅ You should see: `WARNING in app.run_simple Running on http://127.0.0.1:5000`

### Step 3: Open Browser (30 seconds)
Navigate to: **http://localhost:5000**

### Step 4: Login (1 min)
Click the demo credentials shown on login page:
- **Username**: demo
- **Password**: demo123

✅ **You're in!** Now you can:
- 💰 Deposit/Withdraw demo money
- 🎰 Play the Aviator game
- 📊 View transaction history
- ⚙️ (Admin) Access control panel

---

## Playing the Game

1. Go to **Game** tab
2. Click **START GAME** button
3. Enter your bet amount
4. Click **Place Bet**
5. Watch the multiplier rise
6. Click **CASH OUT** before it crashes
   - If you cash out at 2.0x with $100 → You win $200! 🎉
   - If it crashes before you cash out → You lose the bet 😔

---

## Demo Admin Account

If you want to try admin features:
- **Username**: admin
- **Password**: admin123

Admin panel includes:
- View all users
- Credit/Debit user balance
- Monitor transactions
- View game history
- Export data

---

## Stop Server
Press `Ctrl+C` in terminal

---

## Database
Auto-created at: `backend/aviator_demo.db`

---

## Troubleshooting
```bash
# If port 5000 is in use, edit backend/app.py:
app.run(..., port=5001)  # Change to 5001 or any available port
```

---

**Enjoy the demo! 🚀**
