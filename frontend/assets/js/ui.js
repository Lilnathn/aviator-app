/**
 * UI utilities and components for Aviator betting app
 */

class UIManager {
    constructor() {
        this.currentPage = 'login';
        this.setupEventListeners();
    }

    /**
     * Setup global event listeners
     */
    setupEventListeners() {
        // Game events
        window.addEventListener('gameStarted', (e) => this.onGameStarted(e.detail));
        window.addEventListener('gameUpdate', (e) => this.onGameUpdate(e.detail));
        window.addEventListener('gameCrashed', (e) => this.onGameCrashed(e.detail));
        window.addEventListener('betPlaced', (e) => this.onBetPlaced(e.detail));
        window.addEventListener('betWon', (e) => this.onBetWon(e.detail));
        window.addEventListener('betLost', (e) => this.onBetLost(e.detail));
    }

    /**
     * Show page
     */
    showPage(pageName) {
        // Hide all pages
        document.querySelectorAll('[data-page]').forEach(page => {
            page.classList.add('hidden');
        });

        // Show requested page
        const page = document.querySelector(`[data-page="${pageName}"]`);
        if (page) {
            page.classList.remove('hidden');
            this.currentPage = pageName;
        }
    }

    /**
     * Show alert/message
     */
    showAlert(message, type = 'info', duration = 3000) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;

        const container = document.querySelector('[data-alerts]') || document.body;
        container.appendChild(alertDiv);

        if (duration > 0) {
            setTimeout(() => alertDiv.remove(), duration);
        }

        return alertDiv;
    }

    /**
     * Format currency
     */
    formatCurrency(amount) {
        return `$${parseFloat(amount).toFixed(2)}`;
    }

    /**
     * Format multiplier
     */
    formatMultiplier(multiplier) {
        return `${parseFloat(multiplier).toFixed(2)}x`;
    }

    /**
     * Update balance display
     */
    updateBalanceDisplay(balance) {
        const elements = document.querySelectorAll('[data-balance]');
        elements.forEach(el => {
            el.textContent = this.formatCurrency(balance);
        });
    }

    /**
     * Game event handlers
     */
    onGameStarted(gameState) {
        this.showAlert('New game round started!', 'info');
        this.updateMultiplierDisplay(1.0);
    }

    onGameUpdate(gameState) {
        this.updateMultiplierDisplay(gameState.multiplier, gameState.crashed);
    }

    onGameCrashed(detail) {
        const element = document.querySelector('[data-multiplier]');
        if (element) {
            element.classList.add('crashed');
        }
        this.showAlert(`Game crashed at ${this.formatMultiplier(detail.crashPoint)}!`, 'error', 5000);
    }

    onBetPlaced(bet) {
        this.showAlert(`Bet placed: ${this.formatCurrency(bet.amount)}`, 'success');
        this.updateActiveBets();
    }

    onBetWon(detail) {
        const multiplier = detail.bet.cash_out_multiplier || 1;
        this.showAlert(`Won! Cashed out at ${this.formatMultiplier(multiplier)} = ${this.formatCurrency(detail.winnings)}`, 'success', 5000);
    }

    onBetLost(detail) {
        this.showAlert(`Lost! Game crashed at ${this.formatMultiplier(detail.crashPoint)}`, 'error', 5000);
    }

    /**
     * Update multiplier display
     */
    updateMultiplierDisplay(multiplier, crashed = false) {
        const element = document.querySelector('[data-multiplier]');
        if (element) {
            element.textContent = this.formatMultiplier(multiplier);
            element.classList.remove('crashed', 'success');

            if (crashed) {
                element.classList.add('crashed');
            } else if (multiplier > 1.5) {
                element.classList.add('success');
            }
        }
    }

    /**
     * Update active bets display
     */
    updateActiveBets() {
        // This would be called to refresh active bets list
    }

    /**
     * Disable/enable betting controls
     */
    setBettingEnabled(enabled) {
        document.querySelectorAll('[data-bet-controls]').forEach(control => {
            control.disabled = !enabled;
            control.style.opacity = enabled ? '1' : '0.5';
        });
    }

    /**
     * Show loading state
     */
    setLoading(element, loading = true) {
        if (loading) {
            element.disabled = true;
            element.classList.add('loading');
            element.innerHTML = '<span>...</span>';
        } else {
            element.disabled = false;
            element.classList.remove('loading');
        }
    }

    /**
     * Create table row from data
     */
    createTableRow(data, columns) {
        const tr = document.createElement('tr');

        columns.forEach(col => {
            const td = document.createElement('td');
            const value = data[col.key];

            if (col.format) {
                td.innerHTML = col.format(value, data);
            } else {
                td.textContent = value || '-';
            }

            tr.appendChild(td);
        });

        return tr;
    }

    /**
     * Clear table
     */
    clearTable(tableElement) {
        const tbody = tableElement.querySelector('tbody') || tableElement;
        tbody.innerHTML = '';
    }

    /**
     * Format date/time
     */
    formatDateTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString();
    }

    /**
     * Format date only
     */
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString();
    }

    /**
     * Format time only
     */
    formatTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleTimeString();
    }

    /**
     * Abbreviate large numbers
     */
    abbreviateNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(2) + 'M';
        }
        if (num >= 1000) {
            return (num / 1000).toFixed(2) + 'K';
        }
        return num.toFixed(2);
    }

    /**
     * Get percentage change style
     */
    getPercentageClass(value) {
        if (value > 0) return 'positive';
        if (value < 0) return 'negative';
        return 'neutral';
    }

    /**
     * Create status badge
     */
    createStatusBadge(status) {
        const badge = document.createElement('span');
        badge.className = `status-badge status-badge-${status}`;
        badge.textContent = status.toUpperCase();
        return badge;
    }

    /**
     * Create mini chart or indicator
     */
    createMiniChart(data, type = 'trend') {
        const container = document.createElement('div');
        container.className = 'mini-chart';

        // Simplified implementation
        if (type === 'trend') {
            const arrow = data.trend > 0 ? '↑' : '↓';
            container.innerHTML = `<span class="${data.trend > 0 ? 'positive' : 'negative'}">${arrow}</span>`;
        }

        return container;
    }

    /**
     * Handle modal
     */
    showModal(modalId, show = true) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.toggle('show', show);
        }
    }

    closeModal(modalId) {
        this.showModal(modalId, false);
    }

    /**
     * Tab management
     */
    switchTab(tabName) {
        // Hide all tab contents
        document.querySelectorAll('[data-tab-content]').forEach(content => {
            content.classList.remove('active');
        });

        // Remove active class from all tab buttons
        document.querySelectorAll('[data-tab-btn]').forEach(btn => {
            btn.classList.remove('active');
        });

        // Show selected tab
        const tabContent = document.querySelector(`[data-tab-content="${tabName}"]`);
        const tabBtn = document.querySelector(`[data-tab-btn="${tabName}"]`);

        if (tabContent) tabContent.classList.add('active');
        if (tabBtn) tabBtn.classList.add('active');
    }

    /**
     * Form utilities
     */
    getFormData(formElement) {
        const formData = new FormData(formElement);
        const data = {};

        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }

        return data;
    }

    /**
     * Validate required fields
     */
    validateRequired(fields) {
        const errors = [];

        fields.forEach(field => {
            if (!field.value || field.value.trim() === '') {
                errors.push(field.name);
            }
        });

        return errors.length === 0 ? null : errors;
    }

    /**
     * Clear form
     */
    clearForm(formElement) {
        formElement.reset();
        formElement.querySelectorAll('input, textarea, select').forEach(field => {
            field.value = '';
        });
    }
}

// Create global UI manager instance
const ui = new UIManager();
