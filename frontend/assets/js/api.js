/**
 * API Client for Aviator betting application
 * Handles all backend communication
 */

/**
 * Automatically detect the API base URL based on environment
 * For Render deployment: reads from window.CONFIG.API_BASE_URL
 * For local development: defaults to localhost:5000
 * 
 * Configuration:
 * - Local dev: http://localhost:5000/api
 * - Render: https://your-app.onrender.com/api
 * 
 * To use Render API:
 * 1. Add this to index.html before loading api.js:
 *    <script>
 *      window.CONFIG = {
 *        API_BASE_URL: 'https://your-app.onrender.com/api'
 *      };
 *    </script>
 */
const API_BASE_URL = (() => {
    // Check if custom config is set
    if (window.CONFIG && window.CONFIG.API_BASE_URL) {
        return window.CONFIG.API_BASE_URL;
    }
    
    // Auto-detect based on hostname
    const hostname = window.location.hostname;
    const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1';
    
    if (isLocalhost) {
        return 'http://localhost:5000/api';
    } else {
        // For production: use same domain as frontend
        const protocol = window.location.protocol;
        return `${protocol}//${hostname}/api`;
    }
})();

class APIClient {
    constructor() {
        this.token = this.getStoredToken();
    }

    /**
     * Utility method for API calls
     */
    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        // Add token if available
        if (this.token) {
            config.headers['Authorization'] = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok && response.status === 401) {
                this.clearToken();
                window.location.href = '/login';
            }

            return { success: response.ok, data, status: response.status };
        } catch (error) {
            console.error('API Error:', error);
            return { success: false, error: error.message };
        }
    }

    /**
     * Authentication endpoints
     */
    async register(username, email, password) {
        return this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, email, password })
        });
    }

    async login(username, password) {
        const result = await this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });

        if (result.success && result.data.token) {
            this.setToken(result.data.token);
        }

        return result;
    }

    async verifyToken() {
        return this.request('/auth/verify', { method: 'GET' });
    }

    /**
     * Wallet endpoints
     */
    async getBalance() {
        return this.request('/wallet/balance', { method: 'GET' });
    }

    async deposit(amount, provider = 'manual', phoneNumber = '') {
        return this.request('/wallet/deposit', {
            method: 'POST',
            body: JSON.stringify({
                amount,
                provider,
                phone_number: phoneNumber
            })
        });
    }

    async withdraw(amount, method = 'manual') {
        return this.request('/wallet/withdraw', {
            method: 'POST',
            body: JSON.stringify({ amount, method })
        });
    }

    async getTransactions(limit = 50, offset = 0) {
        return this.request(`/wallet/transactions?limit=${limit}&offset=${offset}`, {
            method: 'GET'
        });
    }

    async getPaymentProviders() {
        return this.request('/wallet/providers', { method: 'GET' });
    }

    /**
     * Game endpoints
     */
    async startGame() {
        return this.request('/game/start', { method: 'POST' });
    }

    async getGameState() {
        return this.request('/game/state', { method: 'GET' });
    }

    async placeBet(amount) {
        return this.request('/game/bet', {
            method: 'POST',
            body: JSON.stringify({ amount })
        });
    }

    async cashOut(betId) {
        return this.request('/game/cashout', {
            method: 'POST',
            body: JSON.stringify({ bet_id: betId })
        });
    }

    async triggerCrash() {
        return this.request('/game/crash', { method: 'POST' });
    }

    async getGameHistory(limit = 20) {
        return this.request(`/game/history?limit=${limit}`, { method: 'GET' });
    }

    async getUserGameInfo() {
        return this.request('/game/info', { method: 'GET' });
    }

    async updateMultiplier(elapsedSeconds) {
        return this.request('/game/update-multiplier', {
            method: 'POST',
            body: JSON.stringify({ elapsed_seconds: elapsedSeconds })
        });
    }

    /**
     * Admin endpoints
     */
    async getAdminDashboard() {
        return this.request('/admin/dashboard', { method: 'GET' });
    }

    async listUsers(limit = 20, offset = 0) {
        return this.request(`/admin/users?limit=${limit}&offset=${offset}`, {
            method: 'GET'
        });
    }

    async getUser(userId) {
        return this.request(`/admin/users/${userId}`, { method: 'GET' });
    }

    async creditUser(userId, amount, reason) {
        return this.request(`/admin/users/${userId}/credit`, {
            method: 'POST',
            body: JSON.stringify({ amount, reason })
        });
    }

    async debitUser(userId, amount, reason) {
        return this.request(`/admin/users/${userId}/debit`, {
            method: 'POST',
            body: JSON.stringify({ amount, reason })
        });
    }

    async listTransactions(limit = 50, offset = 0, type = null) {
        let url = `/admin/transactions?limit=${limit}&offset=${offset}`;
        if (type) url += `&type=${type}`;
        return this.request(url, { method: 'GET' });
    }

    async listGames(limit = 20, offset = 0) {
        return this.request(`/admin/games?limit=${limit}&offset=${offset}`, {
            method: 'GET'
        });
    }

    async getGameDetails(gameId) {
        return this.request(`/admin/games/${gameId}`, { method: 'GET' });
    }

    async listPayments(limit = 50, offset = 0, status = null) {
        let url = `/admin/payments?limit=${limit}&offset=${offset}`;
        if (status) url += `&status=${status}`;
        return this.request(url, { method: 'GET' });
    }

    async exportUsers() {
        return this.request('/admin/export/users', { method: 'GET' });
    }

    async exportTransactions() {
        return this.request('/admin/export/transactions', { method: 'GET' });
    }

    /**
     * Token management
     */
    setToken(token) {
        this.token = token;
        localStorage.setItem('auth_token', token);
    }

    getStoredToken() {
        return localStorage.getItem('auth_token');
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('auth_token');
    }

    isAuthenticated() {
        return !!this.token;
    }

    /**
     * User info management
     */
    setUserInfo(user) {
        localStorage.setItem('user_info', JSON.stringify(user));
    }

    getUserInfo() {
        const stored = localStorage.getItem('user_info');
        return stored ? JSON.parse(stored) : null;
    }

    clearUserInfo() {
        localStorage.removeItem('user_info');
    }

    logout() {
        this.clearToken();
        this.clearUserInfo();
    }

    /**
     * Configuration and health
     */
    getAPIConfig() {
        return {
            baseURL: API_BASE_URL,
            environment: window.CONFIG?.environment || 'auto-detected',
            isLocalhost: API_BASE_URL.includes('localhost')
        };
    }

    async getDemoInfo() {
        try {
            const response = await fetch(API_BASE_URL.replace('/api', ''));
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error getting demo info:', error);
            return null;
        }
    }
}

// Create global API instance
const api = new APIClient();
