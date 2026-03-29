# PROJECT STRUCTURE & FILES

## Directory Tree

```
AVIATOR/
├── README.md                          (Main documentation)
├── QUICKSTART.md                      (5-minute setup guide)
├── DEPLOYMENT.md                      (Deployment & demo guide)
├── PAYMENT_INTEGRATION.md             (Payment provider setup)
├── .env.example                       (Environment variables template)
│
├── backend/
│   ├── app.py                        (Main Flask application)
│   ├── requirements.txt              (Python dependencies)
│   ├── aviator_demo.db              (SQLite database - auto-created)
│   │
│   ├── models/
│   │   └── database.py              (All database models)
│   │       ├── User
│   │       ├── Transaction
│   │       ├── GameRound
│   │       ├── Bet
│   │       └── PaymentLog
│   │
│   ├── services/
│   │   ├── auth_service.py          (Auth & JWT logic)
│   │   │   ├── register_user()
│   │   │   ├── login_user()
│   │   │   ├── generate_token()
│   │   │   └── token_required decorator
│   │   │
│   │   ├── wallet_service.py        (Balance & transactions)
│   │   │   ├── get_balance()
│   │   │   ├── deposit()
│   │   │   ├── withdraw()
│   │   │   ├── get_transactions()
│   │   │   └── admin_credit/debit()
│   │   │
│   │   ├── game_service.py          (Game logic)
│   │   │   ├── start_new_round()
│   │   │   ├── place_bet()
│   │   │   ├── cash_out()
│   │   │   ├── process_crash()
│   │   │   ├── update_multiplier()
│   │   │   ├── generate_crash_point()
│   │   │   └── get_game_history()
│   │   │
│   │   └── payment_service.py       (Payment APIs)
│   │       ├── PaymentService (simulated)
│   │       ├── MPesaPaymentProvider (template)
│   │       ├── MTNMoneyProvider (template)
│   │       ├── AirtelMoneyProvider (template)
│   │       ├── TigoMoneyProvider (template)
│   │       └── GenericPaymentProvider (template)
│   │
│   └── routes/
│       ├── auth_routes.py           (Auth endpoints)
│       │   ├── POST /api/auth/register
│       │   ├── POST /api/auth/login
│       │   └── GET /api/auth/verify
│       │
│       ├── wallet_routes.py         (Wallet endpoints)
│       │   ├── GET /api/wallet/balance
│       │   ├── POST /api/wallet/deposit
│       │   ├── POST /api/wallet/withdraw
│       │   ├── GET /api/wallet/transactions
│       │   └── GET /api/wallet/providers
│       │
│       ├── game_routes.py           (Game endpoints)
│       │   ├── POST /api/game/start
│       │   ├── GET /api/game/state
│       │   ├── POST /api/game/bet
│       │   ├── POST /api/game/cashout
│       │   ├── POST /api/game/crash
│       │   ├── GET /api/game/history
│       │   ├── GET /api/game/info
│       │   └── POST /api/game/update-multiplier
│       │
│       └── admin_routes.py          (Admin endpoints)
│           ├── GET /api/admin/dashboard
│           ├── GET /api/admin/users
│           ├── GET /api/admin/users/{id}
│           ├── POST /api/admin/users/{id}/credit
│           ├── POST /api/admin/users/{id}/debit
│           ├── GET /api/admin/transactions
│           ├── GET /api/admin/games
│           ├── GET /api/admin/games/{id}
│           ├── GET /api/admin/payments
│           ├── GET /api/admin/export/users
│           └── GET /api/admin/export/transactions
│
└── frontend/
    ├── index.html                   (Single page app)
    │   ├── div#root (main container)
    │   └── Links to CSS and JS files
    │
    └── assets/
        ├── css/
        │   ├── style.css            (Main styles - 1000+ lines)
        │   │   ├── Colors & themes
        │   │   ├── Layout (grid, sidebar)
        │   │   ├── Forms & inputs
        │   │   ├── Buttons
        │   │   ├── Cards
        │   │   ├── Alerts
        │   │   ├── Auth pages
        │   │   ├── Responsive design
        │   │   └── Animations
        │   │
        │   ├── game.css             (Game styles - 500+ lines)
        │   │   ├── Game board
        │   │   ├── Multiplier display
        │   │   ├── Betting panel
        │   │   ├── Cash out button
        │   │   ├── Game history
        │   │   ├── Stats grid
        │   │   └── Responsive
        │   │
        │   └── admin.css            (Admin panel styles - 500+ lines)
        │       ├── Dashboard stats
        │       ├── Tabs
        │       ├── Forms
        │       ├── User list
        │       ├── Tables
        │       ├── Modals
        │       ├── Pagination
        │       └── Responsive
        │
        └── js/
            ├── api.js               (API client - 300+ lines)
            │   ├── APIClient class
            │   ├── request() method
            │   ├── Auth methods
            │   ├── Wallet methods
            │   ├── Game methods
            │   ├── Admin methods
            │   └── Token management
            │
            ├── game.js              (Game engine - 400+ lines)
            │   ├── GameEngine class
            │   ├── startNewRound()
            │   ├── placeBet()
            │   ├── cashOut()
            │   ├── updateGameState()
            │   ├── generateCrashPoint()
            │   └── Event dispatching
            │
            ├── ui.js                (UI utilities - 400+ lines)
            │   ├── UIManager class
            │   ├── showPage()
            │   ├── showAlert()
            │   ├── Format functions
            │   ├── Update displays
            │   ├── Form helpers
            │   ├── Table creation
            │   └── Modal management
            │
            └── app.js               (Main app logic - 1200+ lines)
                ├── initializeApp()
                ├── renderApp()
                ├── Page renders
                │   ├── renderLoginPage()
                │   ├── renderRegisterPage()
                │   ├── renderDashboard()
                │   ├── renderGamePage()
                │   ├── renderWalletPage()
                │   ├── renderTransactionsPage()
                │   └── renderAdminPage()
                ├── Page navigation
                ├── Login/Register handlers
                ├── Logout
                ├── Game functions
                ├── Wallet functions
                ├── Admin functions
                ├── Export functions
                └── Event listeners
```

---

## File Statistics

### Backend Code
- **app.py**: ~150 lines
- **database.py**: ~250 lines
- **auth_service.py**: ~100 lines
- **wallet_service.py**: ~180 lines
- **game_service.py**: ~280 lines
- **payment_service.py**: ~350 lines
- **auth_routes.py**: ~50 lines
- **wallet_routes.py**: ~80 lines
- **game_routes.py**: ~100 lines
- **admin_routes.py**: ~200 lines
- **Total Backend**: ~1,540 lines of Python

### Frontend Code
- **index.html**: ~20 lines
- **style.css**: ~1,000 lines
- **game.css**: ~500 lines
- **admin.css**: ~500 lines
- **api.js**: ~300 lines
- **game.js**: ~400 lines
- **ui.js**: ~400 lines
- **app.js**: ~1,200 lines
- **Total Frontend**: ~4,320 lines of code

### Documentation
- **README.md**: ~800 lines (comprehensive guide)
- **QUICKSTART.md**: ~100 lines (5-minute guide)
- **DEPLOYMENT.md**: ~500 lines (deployment guide)
- **PAYMENT_INTEGRATION.md**: ~400 lines (payment setup)
- **Total Documentation**: ~1,800 lines

### Total Project
- **Backend**: ~1,540 lines Python
- **Frontend**: ~4,320 lines (HTML/CSS/JS)
- **Documentation**: ~1,800 lines
- **Total**: ~7,660 lines of code + documentation

---

## Key Features by File

### database.py (All Models)
```
✅ User model with password hashing
✅ Transaction model for audit trail
✅ GameRound model for game tracking
✅ Bet model for bet management
✅ PaymentLog model for payment audit
```

### auth_service.py
```
✅ Secure registration with validation
✅ Login with JWT token generation
✅ Token verification
✅ Password hashing & verification
✅ Admin role checking
```

### wallet_service.py
```
✅ Get balance
✅ Deposit demo money
✅ Withdraw demo money
✅ Transaction history
✅ Admin credit/debit
```

### game_service.py
```
✅ Random crash point generation
✅ Multiplier calculation
✅ Bet placement & settlement
✅ Cash-out logic
✅ Game state management
✅ Win/loss calculation
```

### payment_service.py
```
✅ Simulated payments with 90% success rate
✅ Multi-provider support
✅ Payment logging
✅ API integration templates
✅ M-Pesa, MTN, Airtel, Tigo, Rwanda, Zambia
```

### style.css (Main UI)
```
✅ Dark theme colors
✅ Grid layout system
✅ Responsive design
✅ Animations
✅ Dark mode optimized
✅ Modern aesthetics
```

### game.css
```
✅ Game board styling
✅ Multiplier animations
✅ Betting panel
✅ Cash-out button effects
✅ Game history display
✅ Responsive game UI
```

### admin.css
```
✅ Dashboard stats
✅ Tab navigation
✅ User management
✅ Transaction tables
✅ Modal dialogs
✅ Export buttons
```

### api.js (API Client)
```
✅ Fetch-based HTTP client
✅ JWT token management
✅ Error handling
✅ All API endpoints
✅ Request/response caching
```

### game.js (Game Engine)
```
✅ Game state management
✅ Multiplier updates
✅ Bet placement
✅ Cash-out logic
✅ Crash detection
✅ Event system
```

### ui.js (UI Manager)
```
✅ Page navigation
✅ Alert messages
✅ Format utilities
✅ Table creation
✅ Modal management
✅ Form helpers
```

### app.js (Main Logic)
```
✅ Authentication flows
✅ Page rendering
✅ Game integration
✅ Wallet operations
✅ Admin panel
✅ Data export
```

---

## Configuration & Setup Files

- **requirements.txt**: Dependencies list
- **.env.example**: Environment variables template
- **aviator_demo.db**: Auto-created SQLite database

---

## Database Schema

```sql
-- Users Table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE,
    email VARCHAR(120) UNIQUE,
    password_hash VARCHAR(255),
    balance FLOAT,
    created_at DATETIME,
    updated_at DATETIME,
    is_admin BOOLEAN
);

-- Transactions Table
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER FOREIGN KEY,
    transaction_type VARCHAR(20),
    amount FLOAT,
    balance_before FLOAT,
    balance_after FLOAT,
    description VARCHAR(255),
    payment_method VARCHAR(50),
    created_at DATETIME
);

-- Game Rounds Table
CREATE TABLE game_rounds (
    id INTEGER PRIMARY KEY,
    round_number INTEGER UNIQUE,
    crash_point FLOAT,
    started_at DATETIME,
    ended_at DATETIME,
    status VARCHAR(20)
);

-- Bets Table
CREATE TABLE bets (
    id INTEGER PRIMARY KEY,
    user_id INTEGER FOREIGN KEY,
    game_round_id INTEGER FOREIGN KEY,
    bet_amount FLOAT,
    cash_out_multiplier FLOAT,
    result VARCHAR(20),
    winnings FLOAT,
    placed_at DATETIME,
    cash_out_at DATETIME
);

-- Payment Logs Table
CREATE TABLE payment_logs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER FOREIGN KEY,
    provider VARCHAR(50),
    transaction_ref VARCHAR(100) UNIQUE,
    amount FLOAT,
    status VARCHAR(20),
    request_data JSON,
    response_data JSON,
    created_at DATETIME,
    updated_at DATETIME
);
```

---

## API Response Examples

### Successful Login
```json
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "demo",
    "balance": 500.00,
    "is_admin": false
  }
}
```

### Game State
```json
{
  "game": {
    "round_id": 1,
    "multiplier": 2.45,
    "crash_point": 3.82,
    "is_active": true,
    "crashed": false
  }
}
```

### Winning Bet
```json
{
  "success": true,
  "winnings": 250.00,
  "new_balance": 750.00,
  "bet": {
    "id": 1,
    "cash_out_multiplier": 2.5,
    "result": "won"
  }
}
```

---

## Technologies Summary

### Backend
- Python 3.8+
- Flask 2.3.2
- SQLAlchemy ORM
- JWT Authentication
- SQLite Database
- CORS enabled

### Frontend
- Vanilla JavaScript (ES6+)
- HTML5
- CSS3 Grid & Flexbox
- No external framework
- Responsive design
- Dark theme

### Database
- SQLite (built-in)
- Indexed queries
- Relational schema
- Data persistence

### Security
- Password hashing (werkzeug)
- JWT tokens
- Input validation
- CORS protection
- Session management

---

**All files are production-ready and fully functional for school demo purposes!**
