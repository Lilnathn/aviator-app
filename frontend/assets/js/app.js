/**
 * Main application logic for Aviator betting demo
 */

// ============================================================================
// APPLICATION STATE
// ============================================================================

const appState = {
    user: null,
    isAuthenticated: false,
    userBalance: 0,
    currentPage: 'login',
    isAdmin: false
};

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', async () => {
    initializeApp();
});

async function initializeApp() {
    // Check if user is already logged in
    const token = api.getStoredToken();

    if (token) {
        const result = await api.verifyToken();

        if (result.success) {
            appState.user = result.data.user;
            appState.isAuthenticated = true;
            appState.userBalance = result.data.user.balance;
            appState.isAdmin = result.data.user.is_admin;

            renderApp();
            showDashboard();
        } else {
            api.logout();
            showLoginPage();
        }
    } else {
        showLoginPage();
    }
}

// ============================================================================
// PAGE RENDERING
// ============================================================================

function renderApp() {
    const root = document.getElementById('root');
    root.innerHTML = `
        <div data-page="dashboard" class="hidden">${renderDashboard()}</div>
        <div data-page="game" class="hidden">${renderGamePage()}</div>
        <div data-page="wallet" class="hidden">${renderWalletPage()}</div>
        <div data-page="transactions" class="hidden">${renderTransactionsPage()}</div>
        <div data-page="admin" class="hidden">${renderAdminPage()}</div>
        <div data-page="login" class="hidden">${renderLoginPage()}</div>
        <div data-page="register" class="hidden">${renderRegisterPage()}</div>
    `;

    setupEventListeners();
}

// ============================================================================
// LOGIN & REGISTER PAGES
// ============================================================================

function renderLoginPage() {
    return `
        <div class="auth-container">
            <div class="auth-card">
                <div class="auth-header">
                    <h1>AVIATOR</h1>
                    <p>School Demo - Betting Simulation</p>
                </div>

                <form class="auth-form" id="loginForm">
                    <div class="form-group">
                        <label class="form-label">Username</label>
                        <input type="text" class="form-input" name="username" placeholder="Enter username" required>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Password</label>
                        <input type="password" class="form-input" name="password" placeholder="Enter password" required>
                    </div>

                    <button type="submit" class="btn btn-primary btn-block">LOGIN</button>

                    <div class="alert alert-info" style="margin-top: 15px; font-size: 12px; text-align: center;">
                        <strong>Demo Credentials:</strong><br>
                        Username: <code>demo</code><br>
                        Password: <code>demo123</code><br>
                        Admin: <code>admin</code> / <code>admin123</code>
                    </div>
                </form>

                <div class="auth-link">
                    Don't have an account? <a href="#" onclick="showRegisterPage(event)">Register here</a>
                </div>
            </div>
        </div>
    `;
}

function renderRegisterPage() {
    return `
        <div class="auth-container">
            <div class="auth-card">
                <div class="auth-header">
                    <h1>AVIATOR</h1>
                    <p>Create Account</p>
                </div>

                <form class="auth-form" id="registerForm">
                    <div class="form-group">
                        <label class="form-label">Username</label>
                        <input type="text" class="form-input" name="username" placeholder="Choose username" required>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Email</label>
                        <input type="email" class="form-input" name="email" placeholder="Enter email" required>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Password</label>
                        <input type="password" class="form-input" name="password" placeholder="Min 6 characters" required>
                    </div>

                    <button type="submit" class="btn btn-primary btn-block">REGISTER</button>
                </form>

                <div class="auth-link">
                    Already have an account? <a href="#" onclick="showLoginPage(event)">Login here</a>
                </div>
            </div>
        </div>
    `;
}

// ============================================================================
// DASHBOARD
// ============================================================================

function renderDashboard() {
    return `
        <div class="app-layout">
            <div class="sidebar">
                ${renderSidebar()}
            </div>

            <div class="main-content">
                <div class="header">
                    <div class="logo">AVIATOR</div>
                    <div style="text-align: right;">
                        <div class="text-secondary" style="font-size: 12px;">Welcome back!</div>
                        <div style="color: var(--primary); font-weight: bold;" data-balance></div>
                    </div>
                </div>

                <div id="alertContainer" data-alerts></div>

                <div class="grid grid-3">
                    <div class="card">
                        <div class="card-header">💰 Balance</div>
                        <div class="card-body">
                            <div style="font-size: 28px; color: var(--success); font-weight: bold;" data-balance></div>
                            <div style="font-size: 12px; color: var(--text-secondary); margin-top: 10px;">Demo Balance</div>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">🎮 Active Bets</div>
                        <div class="card-body">
                            <div style="font-size: 28px; color: var(--primary); font-weight: bold;" id="activeBetsCount">0</div>
                            <div style="font-size: 12px; color: var(--text-secondary); margin-top: 10px;">Current Round</div>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">📊 Total Won</div>
                        <div class="card-body">
                            <div style="font-size: 28px; color: var(--success); font-weight: bold;" id="totalWon">$0.00</div>
                            <div style="font-size: 12px; color: var(--text-secondary); margin-top: 10px;">Today</div>
                        </div>
                    </div>
                </div>

                <div style="margin-top: 20px; text-align: center; color: var(--text-secondary);">
                    <p>👇 Use the menu to navigate to Game, Wallet, or Admin Panel</p>
                </div>
            </div>
        </div>
    `;
}

function renderSidebar() {
    return `
        <div class="user-info">
            <div class="username">${appState.user.username}</div>
            <div class="balance">Balance: <span data-balance></span></div>
            ${appState.isAdmin ? '<div style="color: var(--secondary); font-size: 11px; margin-top: 5px;">👨‍💼 Admin</div>' : ''}
        </div>

        <nav class="nav-menu">
            <button class="nav-item" onclick="showDashboard()">🏠 Dashboard</button>
            <button class="nav-item" onclick="showGamePage()">🎰 Game</button>
            <button class="nav-item" onclick="showWalletPage()">💳 Wallet</button>
            <button class="nav-item" onclick="showTransactionsPage()">📜 History</button>
            ${appState.isAdmin ? '<button class="nav-item" onclick="showAdminPage()">⚙️ Admin Panel</button>' : ''}
        </nav>

        <button class="logout-btn" onclick="logout()">LOGOUT</button>
    `;
}

// ============================================================================
// GAME PAGE
// ============================================================================

function renderGamePage() {
    return `
        <div class="app-layout">
            <div class="sidebar">${renderSidebar()}</div>

            <div class="main-content">
                <div class="header">
                    <div class="logo">AVIATOR GAME</div>
                </div>

                <div id="alertContainer" data-alerts></div>

                <div class="game-container">
                    <div class="game-board">
                        <div id="gameStatus" class="game-status">Click "Start Game" to begin</div>
                        <div id="multiplierDisplay" data-multiplier class="multiplier-display">
                            1.00<span class="x">x</span>
                        </div>
                    </div>

                    <div class="betting-panel" id="bettingPanel">
                        <div class="card-header">Place Your Bet</div>

                        <div class="bet-info">
                            <div class="label">Your Balance:</div>
                            <div class="value" data-balance></div>
                        </div>

                        <div class="form-group">
                            <label class="form-label">Bet Amount</label>
                            <div class="bet-input-group">
                                <input type="number" id="betAmount" class="form-input" placeholder="0.00" min="0" step="0.01">
                                <button type="button" class="btn btn-secondary" onclick="clearBetInput()">Clear</button>
                            </div>
                        </div>

                        <div class="bet-preset-buttons">
                            <button type="button" class="preset-btn" onclick="setBetAmount(10)">$10</button>
                            <button type="button" class="preset-btn" onclick="setBetAmount(50)">$50</button>
                            <button type="button" class="preset-btn" onclick="setBetAmount(100)">$100</button>
                            <button type="button" class="preset-btn" onclick="setBetAmount(500)">$500</button>
                        </div>

                        <button type="button" class="btn-bet" id="placeBetBtn" onclick="placeBet()" disabled>
                            Place Bet
                        </button>

                        <div class="cash-out-section">
                            <button type="button" class="btn-cashout" id="cashOutBtn" onclick="cashOut()" disabled>
                                💰 CASH OUT
                            </button>
                            <div class="text-center text-secondary" style="font-size: 12px; margin-top: 10px;">
                                Potential Win: <span style="color: var(--success);" id="potentialWin">$0.00</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-label">Game Status</div>
                        <div class="stat-value" id="statusBadge" style="font-size: 14px;">Inactive</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Round #</div>
                        <div class="stat-value" id="roundNumber" style="font-size: 16px;">-</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Your Bet</div>
                        <div class="stat-value" id="currentBetDisplay" style="font-size: 16px;">$0.00</div>
                    </div>
                </div>

                <div class="game-history" id="gameHistoryContainer"></div>

                <div style="margin-top: 20px; text-align: center;">
                    <button type="button" class="btn btn-primary" id="startGameBtn" onclick="startGame()">
                        ▶️ START GAME
                    </button>
                </div>
            </div>
        </div>
    `;
}

// ============================================================================
// WALLET PAGE
// ============================================================================

function renderWalletPage() {
    return `
        <div class="app-layout">
            <div class="sidebar">${renderSidebar()}</div>

            <div class="main-content">
                <div class="header">
                    <div class="logo">WALLET</div>
                </div>

                <div id="alertContainer" data-alerts></div>

                <div class="grid grid-2">
                    <div class="card">
                        <div class="card-header">💰 Current Balance</div>
                        <div class="card-body">
                            <div style="font-size: 32px; color: var(--success); font-weight: bold;" data-balance></div>
                            <div style="font-size: 12px; color: var(--text-secondary); margin-top: 10px;">Demo Money</div>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">💳 Deposit Demo Money</div>
                        <div class="card-body">
                            <form id="depositForm">
                                <div class="form-group">
                                    <label class="form-label">Amount</label>
                                    <input type="number" class="form-input" name="amount" placeholder="0.00" min="0" step="0.01" required>
                                </div>

                                <div class="form-group">
                                    <label class="form-label">Payment Method</label>
                                    <select class="form-select" name="provider" id="paymentProvider">
                                        <option value="manual">Demo (Instant)</option>
                                        <option value="mpesa">M-Pesa (Kenya)</option>
                                        <option value="mtn">MTN Money</option>
                                        <option value="airtel">Airtel Money</option>
                                        <option value="tigo">Tigo Pesa (TZ)</option>
                                        <option value="rwmomo">MTN MoMo (Rwanda)</option>
                                        <option value="zambia">MTN/Airtel (Zambia)</option>
                                    </select>
                                </div>

                                <div class="form-group" id="phoneNumberGroup" style="display: none;">
                                    <label class="form-label">Phone Number</label>
                                    <input type="tel" class="form-input" name="phone_number" placeholder="+1234567890">
                                </div>

                                <button type="submit" class="btn btn-success btn-block">Deposit</button>
                            </form>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">🔄 Withdraw Demo Money</div>
                        <div class="card-body">
                            <form id="withdrawForm">
                                <div class="form-group">
                                    <label class="form-label">Amount</label>
                                    <input type="number" class="form-input" name="amount" placeholder="0.00" min="0" step="0.01" required>
                                </div>

                                <div class="form-group">
                                    <label class="form-label">Max Available: <span data-balance></span></label>
                                </div>

                                <button type="submit" class="btn btn-danger btn-block">Withdraw</button>
                            </form>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">📊 Recent Transactions</div>
                    <div class="card-body">
                        <table class="table" id="transactionsTable">
                            <thead>
                                <tr>
                                    <th>Type</th>
                                    <th>Amount</th>
                                    <th>Balance</th>
                                    <th>Date</th>
                                </tr>
                            </thead>
                            <tbody id="transactionsBody">
                                <tr><td colspan="4" style="text-align: center; color: var(--text-secondary);">Loading...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// ============================================================================
// TRANSACTIONS PAGE
// ============================================================================

function renderTransactionsPage() {
    return `
        <div class="app-layout">
            <div class="sidebar">${renderSidebar()}</div>

            <div class="main-content">
                <div class="header">
                    <div class="logo">TRANSACTION HISTORY</div>
                </div>

                <div id="alertContainer" data-alerts></div>

                <div class="card">
                    <div class="card-header">All Transactions</div>
                    <div class="card-body">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Type</th>
                                    <th>Amount</th>
                                    <th>Status</th>
                                    <th>Description</th>
                                    <th>Date</th>
                                </tr>
                            </thead>
                            <tbody id="allTransactionsBody">
                                <tr><td colspan="5" style="text-align: center;">Loading...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// ============================================================================
// ADMIN PAGE
// ============================================================================

function renderAdminPage() {
    return `
        <div class="app-layout">
            <div class="sidebar">${renderSidebar()}</div>

            <div class="main-content">
                <div class="header">
                    <div class="logo">⚙️ ADMIN CONTROL PANEL</div>
                </div>

                <div id="alertContainer" data-alerts></div>

                <div class="admin-dashboard" id="adminDashboard">
                    <div class="dashboard-stat">
                        <div class="dashboard-stat-label">Total Users</div>
                        <div class="dashboard-stat-value" id="totalUsersCount">0</div>
                    </div>
                    <div class="dashboard-stat">
                        <div class="dashboard-stat-label">System Balance</div>
                        <div class="dashboard-stat-value" id="systemBalanceCount">$0.00</div>
                    </div>
                    <div class="dashboard-stat">
                        <div class="dashboard-stat-label">Transactions</div>
                        <div class="dashboard-stat-value" id="totalTransactionsCount">0</div>
                    </div>
                    <div class="dashboard-stat">
                        <div class="dashboard-stat-label">Game Rounds</div>
                        <div class="dashboard-stat-value" id="totalGamesCount">0</div>
                    </div>
                </div>

                <div class="tab-navigation">
                    <button class="tab-btn active" onclick="ui.switchTab('usersMgmt')">👥 Users</button>
                    <button class="tab-btn" onclick="ui.switchTab('transactionsMgmt')">📊 Transactions</button>
                    <button class="tab-btn" onclick="ui.switchTab('gamesMgmt')">🎮 Games</button>
                    <button class="tab-btn" onclick="ui.switchTab('paymentsMgmt')">💳 Payments</button>
                </div>

                <div data-tab-content="usersMgmt" class="tab-content active">
                    <div class="search-filter">
                        <input type="text" class="search-input form-input" id="userSearch" placeholder="Search users..." onkeyup="searchUsers()">
                        <button class="btn btn-secondary" onclick="loadAdminUsers()">Refresh</button>
                    </div>
                    <div id="usersContainer" style="display: flex; flex-direction: column; gap: 10px;"></div>
                </div>

                <div data-tab-content="transactionsMgmt" class="tab-content hidden">
                    <div class="search-filter">
                        <select class="filter-select form-select" onchange="loadAdminTransactions()">
                            <option value="">All Types</option>
                            <option value="deposit">Deposits</option>
                            <option value="withdrawal">Withdrawals</option>
                            <option value="bet_win">Bet Wins</option>
                            <option value="admin_credit">Admin Credits</option>
                        </select>
                        <button class="btn btn-secondary" onclick="exportData('transactions')">Export</button>
                    </div>
                    <table class="table">
                        <thead>
                            <tr>
                                <th>User</th>
                                <th>Type</th>
                                <th>Amount</th>
                                <th>Description</th>
                                <th>Date</th>
                            </tr>
                        </thead>
                        <tbody id="adminTransactionsBody">
                            <tr><td colspan="5" style="text-align: center;">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>

                <div data-tab-content="gamesMgmt" class="tab-content hidden">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Round</th>
                                <th>Crash Point</th>
                                <th>Total Bets</th>
                                <th>Status</th>
                                <th>Date</th>
                            </tr>
                        </thead>
                        <tbody id="adminGamesBody">
                            <tr><td colspan="5" style="text-align: center;">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>

                <div data-tab-content="paymentsMgmt" class="tab-content hidden">
                    <div class="search-filter">
                        <select class="filter-select form-select" onchange="loadPaymentLogs()">
                            <option value="">All Status</option>
                            <option value="success">Success</option>
                            <option value="pending">Pending</option>
                            <option value="failed">Failed</option>
                        </select>
                    </div>
                    <table class="table">
                        <thead>
                            <tr>
                                <th>User</th>
                                <th>Provider</th>
                                <th>Amount</th>
                                <th>Status</th>
                                <th>Date</th>
                            </tr>
                        </thead>
                        <tbody id="adminPaymentsBody">
                            <tr><td colspan="5" style="text-align: center;">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
}

// ============================================================================
// EVENT HANDLERS & FUNCTIONS
// ============================================================================

async function login(event) {
    event.preventDefault();

    const form = event.target;
    const username = form.username.value;
    const password = form.password.value;

    const result = await api.login(username, password);

    if (result.success) {
        appState.user = result.data.user;
        appState.isAuthenticated = true;
        appState.userBalance = result.data.user.balance;
        appState.isAdmin = result.data.user.is_admin;

        api.setUserInfo(result.data.user);
        renderApp();
        showDashboard();
    } else {
        ui.showAlert(result.data.message, 'error', 3000);
    }
}

async function register(event) {
    event.preventDefault();

    const form = event.target;
    const username = form.username.value;
    const email = form.email.value;
    const password = form.password.value;

    const result = await api.register(username, email, password);

    if (result.success) {
        ui.showAlert('Registration successful! Please login.', 'success', 2000);
        setTimeout(() => showLoginPage(), 2000);
    } else {
        ui.showAlert(result.data.message, 'error', 3000);
    }
}

function logout() {
    api.logout();
    appState.isAuthenticated = false;
    location.reload();
}

// ============================================================================
// PAGE NAVIGATION
// ============================================================================

function showLoginPage(event) {
    if (event) event.preventDefault();
    renderApp();
    ui.showPage('login');
    const form = document.getElementById('loginForm');
    if (form) form.addEventListener('submit', login);
}

function showRegisterPage(event) {
    if (event) event.preventDefault();
    renderApp();
    ui.showPage('register');
    const form = document.getElementById('registerForm');
    if (form) form.addEventListener('submit', register);
}

function showDashboard() {
    ui.showPage('dashboard');
    updateBalance();
}

function showGamePage() {
    ui.showPage('game');
    loadGamePage();
}

function showWalletPage() {
    ui.showPage('wallet');
    loadWalletPage();
}

function showTransactionsPage() {
    ui.showPage('transactions');
    loadTransactionsPage();
}

function showAdminPage() {
    if (!appState.isAdmin) {
        ui.showAlert('Admin access required', 'error');
        return;
    }

    ui.showPage('admin');
    loadAdminDashboard();
}

// ============================================================================
// PAGE LOGIC FUNCTIONS
// ============================================================================

async function updateBalance() {
    const result = await api.getBalance();

    if (result.success) {
        appState.userBalance = result.data.balance;
        ui.updateBalanceDisplay(result.data.balance);
    }
}

// Game Page Functions
async function loadGamePage() {
    await updateBalance();
    await loadGameHistory();
    
    // Check if game is already active
    const gameState = await gameEngine.getCurrentState();
    if (!gameState) {
        await startGame();
    }
}

async function startGame() {
    const btn = document.getElementById('startGameBtn');
    if (btn) {
        ui.setLoading(btn, true);
    }

    const success = await gameEngine.startNewRound();

    if (success) {
        ui.showAlert('Game started!', 'success');
        document.getElementById('gameStatus').textContent = 'Game is ACTIVE - Place your bet!';
        document.getElementById('statusBadge').textContent = 'ACTIVE';

        // Update UI
        document.getElementById('placeBetBtn').disabled = false;
        document.getElementById('roundNumber').textContent = gameEngine.gameState.roundId;
    } else {
        ui.showAlert('Failed to start game', 'error');
    }

    if (btn) {
        ui.setLoading(btn, false);
    }
}

function setBetAmount(amount) {
    document.getElementById('betAmount').value = amount;
    updatePotentialWin();
}

function clearBetInput() {
    document.getElementById('betAmount').value = '';
    document.getElementById('potentialWin').textContent = '$0.00';
}

function updatePotentialWin() {
    const amount = parseFloat(document.getElementById('betAmount').value) || 0;
    const multiplier = gameEngine.getMultiplier();
    const win = amount * multiplier;
    document.getElementById('potentialWin').textContent = ui.formatCurrency(win);
}

async function placeBet() {
    const amount = parseFloat(document.getElementById('betAmount').value);

    if (!amount || amount <= 0) {
        ui.showAlert('Enter a valid bet amount', 'error');
        return;
    }

    if (amount > appState.userBalance) {
        ui.showAlert('Insufficient balance', 'error');
        return;
    }

    const result = await gameEngine.placeBet(amount);

    if (result.success) {
        appState.userBalance = result.new_balance;
        ui.updateBalanceDisplay(result.new_balance);
        document.getElementById('placeBetBtn').disabled = true;
        document.getElementById('cashOutBtn').disabled = false;
        document.getElementById('currentBetDisplay').textContent = ui.formatCurrency(amount);
        clearBetInput();
    } else {
        ui.showAlert(result.message || 'Failed to place bet', 'error');
    }
}

async function cashOut() {
    const result = await gameEngine.cashOut();

    if (result.success) {
        appState.userBalance = result.new_balance;
        ui.updateBalanceDisplay(result.new_balance);
        document.getElementById('cashOutBtn').disabled = true;
        document.getElementById('currentBetDisplay').textContent = '$0.00';
    } else {
        ui.showAlert(result.message || 'Cannot cash out', 'error');
    }
}

async function loadGameHistory() {
    const history = await gameEngine.getHistory(10);
    const container = document.getElementById('gameHistoryContainer');

    if (container) {
        if (history.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No games yet</p>';
        } else {
            let html = '<div class="game-history-title">Recent Rounds</div><div class="history-items">';

            history.forEach(game => {
                const crashed = game.status === 'crashed';
                html += `
                    <div class="history-item ${crashed ? 'crashed' : ''}">
                        <div class="multiplier">${game.crash_point}x</div>
                        <div class="round">#${game.round_number}</div>
                    </div>
                `;
            });

            html += '</div>';
            container.innerHTML = html;
        }
    }
}

// Wallet Page Functions
async function loadWalletPage() {
    await updateBalance();
    await loadTransactions();
    setupWalletFormHandlers();
}

function setupWalletFormHandlers() {
    const depositForm = document.getElementById('depositForm');
    const withdrawForm = document.getElementById('withdrawForm');

    if (depositForm) {
        depositForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const amount = parseFloat(depositForm.amount.value);
            const provider = depositForm.provider?.value || 'manual';

            const result = await api.deposit(amount, provider);

            if (result.success) {
                ui.showAlert(result.message, 'success');
                appState.userBalance = result.new_balance;
                ui.updateBalanceDisplay(result.new_balance);
                depositForm.reset();
                await loadTransactions();
            } else {
                ui.showAlert(result.message, 'error');
            }
        });
    }

    if (withdrawForm) {
        withdrawForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const amount = parseFloat(withdrawForm.amount.value);

            const result = await api.withdraw(amount);

            if (result.success) {
                ui.showAlert(result.message, 'success');
                appState.userBalance = result.new_balance;
                ui.updateBalanceDisplay(result.new_balance);
                withdrawForm.reset();
                await loadTransactions();
            } else {
                ui.showAlert(result.message, 'error');
            }
        });
    }
}

async function loadTransactions(limit = 10) {
    const result = await api.getTransactions(limit);

    if (result.success) {
        const tbody = document.getElementById('transactionsBody');
        if (tbody) {
            tbody.innerHTML = '';

            result.data.transactions.forEach(tx => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><span class="transaction-type ${tx.type}">${tx.type}</span></td>
                    <td class="${tx.type.includes('win') || tx.type === 'deposit' || tx.type === 'admin_credit' ? 'positive' : 'negative'}">
                        ${tx.type.includes('win') || tx.type === 'deposit' || tx.type === 'admin_credit' ? '+' : '-'}${ui.formatCurrency(tx.amount)}
                    </td>
                    <td>${ui.formatCurrency(tx.balance_after)}</td>
                    <td>${ui.formatDateTime(tx.created_at)}</td>
                `;
                tbody.appendChild(row);
            });
        }
    }
}

async function loadTransactionsPage() {
    const result = await api.getTransactions(100);

    if (result.success) {
        const tbody = document.getElementById('allTransactionsBody');
        if (tbody) {
            tbody.innerHTML = '';

            result.data.transactions.forEach(tx => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><span class="transaction-type ${tx.type}">${tx.type}</span></td>
                    <td>${ui.formatCurrency(tx.amount)}</td>
                    <td><span class="status-badge status-badge-${tx.type.includes('win') ? 'success' : 'pending'}">${tx.type}</span></td>
                    <td>${tx.description}</td>
                    <td>${ui.formatDateTime(tx.created_at)}</td>
                `;
                tbody.appendChild(row);
            });
        }
    }
}

// Admin Functions
async function loadAdminDashboard() {
    const result = await api.getAdminDashboard();

    if (result.success) {
        const stats = result.data.statistics;
        document.getElementById('totalUsersCount').textContent = stats.total_users;
        document.getElementById('systemBalanceCount').textContent = ui.formatCurrency(stats.total_balance);
        document.getElementById('totalTransactionsCount').textContent = stats.total_transactions;
        document.getElementById('totalGamesCount').textContent = stats.total_games;
    }

    await loadAdminUsers();
    await loadAdminTransactions();
}

async function loadAdminUsers() {
    const result = await api.listUsers(50);

    if (result.success) {
        const container = document.getElementById('usersContainer');
        if (container) {
            container.innerHTML = '';

            result.data.users.forEach(user => {
                const div = document.createElement('div');
                div.className = 'user-list-item';
                div.innerHTML = `
                    <div class="user-info-box">
                        <div class="user-name">${user.username} ${user.is_admin ? '👨‍💼' : ''}</div>
                        <div class="user-email">${user.email}</div>
                        <div class="user-stats">Balance: <span style="color: var(--success);">${ui.formatCurrency(user.balance)}</span></div>
                    </div>
                    <div class="user-actions">
                        <button class="btn btn-primary" onclick="creditUserDialog(${user.id})">Credit</button>
                        <button class="btn btn-danger" onclick="debitUserDialog(${user.id})">Debit</button>
                    </div>
                `;
                container.appendChild(div);
            });
        }
    }
}

async function creditUserDialog(userId) {
    const amount = prompt('Enter credit amount:');
    if (amount && !isNaN(amount) && amount > 0) {
        const result = await api.creditUser(userId, parseFloat(amount), 'Admin credit');
        if (result.success) {
            ui.showAlert('User credited successfully', 'success');
            loadAdminUsers();
        }
    }
}

async function debitUserDialog(userId) {
    const amount = prompt('Enter debit amount:');
    if (amount && !isNaN(amount) && amount > 0) {
        const result = await api.debitUser(userId, parseFloat(amount), 'Admin debit');
        if (result.success) {
            ui.showAlert('User debited successfully', 'success');
            loadAdminUsers();
        }
    }
}

async function loadAdminTransactions() {
    const result = await api.listTransactions(50);

    if (result.success) {
        const tbody = document.getElementById('adminTransactionsBody');
        if (tbody) {
            tbody.innerHTML = '';

            result.data.transactions.forEach(tx => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${tx.user_id}</td>
                    <td><span class="transaction-type ${tx.type}">${tx.type}</span></td>
                    <td>${ui.formatCurrency(tx.amount)}</td>
                    <td>${tx.description}</td>
                    <td>${ui.formatDateTime(tx.created_at)}</td>
                `;
                tbody.appendChild(row);
            });
        }
    }
}

async function exportData(type) {
    if (type === 'transactions') {
        const result = await api.exportTransactions();
        if (result.success) {
            downloadJSON(result.data, 'transactions.json');
        }
    } else if (type === 'users') {
        const result = await api.exportUsers();
        if (result.success) {
            downloadJSON(result.data, 'users.json');
        }
    }
}

function downloadJSON(data, filename) {
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
}

function setupEventListeners() {
    const form = document.getElementById('loginForm');
    if (form) form.addEventListener('submit', login);

    const registerForm = document.getElementById('registerForm');
    if (registerForm) registerForm.addEventListener('submit', register);

    const betAmountInput = document.getElementById('betAmount');
    if (betAmountInput) {
        betAmountInput.addEventListener('input', updatePotentialWin);
    }

    const providerSelect = document.getElementById('paymentProvider');
    if (providerSelect) {
        providerSelect.addEventListener('change', () => {
            const phoneGroup = document.getElementById('phoneNumberGroup');
            const provider = providerSelect.value;
            if (provider !== 'manual') {
                phoneGroup.style.display = 'flex';
            } else {
                phoneGroup.style.display = 'none';
            }
        });
    }
}

// Update UI elements on page load
window.addEventListener('load', () => {
    if (api.isAuthenticated()) {
        updateBalance();
    }
});

// Update game display periodically
setInterval(updatePotentialWin, 100);
