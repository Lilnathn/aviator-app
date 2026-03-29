/**
 * Game engine and logic for Aviator betting game
 */

class GameEngine {
    constructor() {
        this.gameState = {
            roundId: null,
            multiplier: 1.0,
            crashPoint: null,
            isActive: false,
            crashed: false,
            startTime: null,
            elapsedTime: 0
        };

        this.currentBet = {
            betId: null,
            amount: 0,
            placedAt: null,
            cashOutMultiplier: null
        };

        this.gameHistory = [];
        this.updateInterval = null;
        this.isRunning = false;
    }

    /**
     * Start a new game round
     */
    async startNewRound() {
        try {
            const result = await api.startGame();

            if (result.success) {
                const gameState = result.data.game;
                this.gameState = {
                    roundId: gameState.round_id,
                    multiplier: 1.0,
                    crashPoint: gameState.crash_point,
                    isActive: gameState.is_active,
                    crashed: false,
                    startTime: Date.now(),
                    elapsedTime: 0
                };

                this.isRunning = true;
                this.startGameLoop();
                window.dispatchEvent(new CustomEvent('gameStarted', { detail: this.gameState }));
                return true;
            }

            return false;
        } catch (error) {
            console.error('Error starting game:', error);
            return false;
        }
    }

    /**
     * Place a bet on current round
     */
    async placeBet(amount) {
        if (!this.gameState.isActive) {
            return { success: false, message: 'No active game' };
        }

        try {
            const result = await api.placeBet(amount);

            if (result.success) {
                const bet = result.data.bet;
                this.currentBet = {
                    betId: bet.id,
                    amount: bet.bet_amount,
                    placedAt: new Date(bet.placed_at),
                    cashOutMultiplier: null
                };

                window.dispatchEvent(new CustomEvent('betPlaced', { detail: this.currentBet }));
                return { success: true, bet };
            }

            return result.data;
        } catch (error) {
            console.error('Error placing bet:', error);
            return { success: false, message: error.message };
        }
    }

    /**
     * Cash out of current bet
     */
    async cashOut() {
        if (!this.currentBet.betId) {
            return { success: false, message: 'No active bet' };
        }

        try {
            const result = await api.cashOut(this.currentBet.betId);

            if (result.success) {
                const bet = result.data.bet;
                this.currentBet.cashOutMultiplier = bet.cash_out_multiplier;

                window.dispatchEvent(new CustomEvent('betWon', {
                    detail: {
                        bet,
                        winnings: result.data.winnings
                    }
                }));

                this.currentBet = {
                    betId: null,
                    amount: 0,
                    placedAt: null,
                    cashOutMultiplier: null
                };

                return { success: true, ...result.data };
            }

            return result.data;
        } catch (error) {
            console.error('Error cashing out:', error);
            return { success: false, message: error.message };
        }
    }

    /**
     * Main game loop - update multiplier periodically
     */
    startGameLoop() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }

        // Update every 100ms for smooth animation
        this.updateInterval = setInterval(() => {
            this.updateGameState();
        }, 100);
    }

    /**
     * Update game state (multiplier, crash detection)
     */
    async updateGameState() {
        if (!this.gameState.isActive || this.gameState.crashed) {
            return;
        }

        try {
            this.gameState.elapsedTime = (Date.now() - this.gameState.startTime) / 1000;

            // Get updated multiplier from server
            const result = await api.updateMultiplier(this.gameState.elapsedTime);

            if (result.success) {
                const data = result.data;
                this.gameState.multiplier = data.multiplier;

                if (data.crashed) {
                    this.gameState.crashed = true;
                    this.gameState.isActive = false;
                    this.crashGame(data.crash_point);
                }

                window.dispatchEvent(new CustomEvent('gameUpdate', { detail: this.gameState }));
            }
        } catch (error) {
            console.error('Error updating game state:', error);
        }
    }

    /**
     * Handle game crash
     */
    async crashGame(crashPoint) {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }

        this.isRunning = false;

        // If user had active bet and didn't cash out, they lose
        if (this.currentBet.betId && !this.currentBet.cashOutMultiplier) {
            window.dispatchEvent(new CustomEvent('betLost', {
                detail: {
                    betAmount: this.currentBet.amount,
                    crashPoint
                }
            }));

            this.currentBet = {
                betId: null,
                amount: 0,
                placedAt: null,
                cashOutMultiplier: null
            };
        }

        window.dispatchEvent(new CustomEvent('gameCrashed', {
            detail: {
                crashPoint,
                multiplier: this.gameState.multiplier
            }
        }));

        // Auto-start next round after delay (optional)
        setTimeout(() => {
            this.startNewRound();
        }, 3000);
    }

    /**
     * Get game history
     */
    async getHistory(limit = 20) {
        try {
            const result = await api.getGameHistory(limit);

            if (result.success) {
                this.gameHistory = result.data.rounds;
                return this.gameHistory;
            }

            return [];
        } catch (error) {
            console.error('Error getting game history:', error);
            return [];
        }
    }

    /**
     * Get current game state
     */
    async getCurrentState() {
        try {
            const result = await api.getGameState();

            if (result.success) {
                return result.data.game;
            }

            return null;
        } catch (error) {
            console.error('Error getting game state:', error);
            return null;
        }
    }

    /**
     * Stop the game loop
     */
    stop() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }

        this.isRunning = false;
    }

    /**
     * Get current multiplier
     */
    getMultiplier() {
        return this.gameState.multiplier;
    }

    /**
     * Check if game is active
     */
    isGameActive() {
        return this.gameState.isActive;
    }

    /**
     * Check if game has crashed
     */
    hasGameCrashed() {
        return this.gameState.crashed;
    }

    /**
     * Calculate potential winnings
     */
    calculateWinnings(betAmount, multiplier) {
        return betAmount * multiplier;
    }
}

// Create global game engine instance
const gameEngine = new GameEngine();
