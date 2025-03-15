import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useGameStore = defineStore('game', {
    state: () => ({
        game: null,
        loading: false,
        error: null,
    }),

    actions: {
        async fetchGame() {
            this.loading = true;
            try {
                const response = await fetch('/api/game');
                this.game = await response.json();
                if (this.game.message == 'No game in progress') {
                    this.game = null;
                    this.error = 'No game in progress';
                }
            } catch (error) {
                this.error = error;
            } finally {
                this.loading = false;
            }
        },
    },
})

export const useTimerStore = defineStore('timer', {
    state: () => ({
        time: ref(60.00),
        interval: null,
        status: null,
    }),

    actions: {
        newTimer(time) {
            this.time = time;
        },

        startTimer() {
            const INTERVAL = 0.3
            if (this.interval) {
                clearInterval(this.interval);
            }
            this.interval = setInterval(() => {
                if (this.time > 0) {
                    this.time -= INTERVAL;
                }
            }, INTERVAL * 1000);
        },

        stopTimer() {
            clearInterval(this.interval);
            this.interval = null;
        },

        resetTimer() {
            this.time = 0;
            if (this.interval) {
                clearInterval(this.interval);
                this.interval = null;
            }
        },

        updateTime(time, status) {
            this.time = time;
            const oldStatus = this.status;

            if (oldStatus !== status) {
                this.status = status;
                if (status == 'pause') {
                    this.stopTimer();
                } else {
                    this.startTimer();
                }
            }
        }
    },
})