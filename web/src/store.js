import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSettingsStore = defineStore('settings', {
    state: () => ({
        rulesets: [],
        tableprests: [],
        error: null
    }),

    actions: {
        async fetchTablePresetsRulesets() {
            try {
                const responseTablePresets = await fetch('/api/table')
                this.tableprests = await responseTablePresets.json()

                const responseRulesets = await fetch('/api/ruleset')
                this.rulesets = await responseRulesets.json()
            } catch (error) {
                this.error = error
            }
        },
        async addTablePreset(name, points, colors, min_area_threshold) {
            try {
                const data = {
                    'name': name,
                    'points': points,
                    'colors': colors,
                    'min_area_threshold': min_area_threshold
                }
                console.log(data)
                const response = await fetch('/api/table', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                })
                if (response.status === 200) {
                    return this.fetchTablePresetsRulesets();
                } else {
                    console.error('Error:', response.statusText);
                    return false;
                }
            } catch (error) {
                this.error = error
            }
        },
        async deleteTablePreset(id) {
            try {
                const response = await fetch(`/api/table/${id}`, {
                    method: 'DELETE'
                })
                if (response.status === 200) {
                    this.fetchTablePresetsRulesets()
                    return true
                } else {
                    console.error('Error:', response.statusText);
                    return false;
                }
            } catch (error) {
                this.error = error
            }
        },
        async addRuleset(name, initial_duration, turn_duration, allarm_time, increment_duration, max_increment_for_match) {
            try {
                const data = {
                    'name': name,
                    'initial_duration': initial_duration,
                    'turn_duration': turn_duration,
                    'allarm_time': allarm_time,
                    'increment_duration': increment_duration,
                    'max_increment_for_match': max_increment_for_match
                }
                console.log(data)
                const response = await fetch('/api/ruleset', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                })
                if (response.status === 200) {
                    return this.fetchTablePresetsRulesets();
                } else {
                    console.error('Error:', response.statusText);
                    return false;
                }
            } catch (error) {
                this.error = error
            }
        },
        async deleteRuleset(id) {
            try {
                const response = await fetch(`/api/ruleset/${id}`, {
                    method: 'DELETE'
                })
                if (response.status === 200) {
                    this.fetchTablePresetsRulesets()
                    return true
                } else {
                    console.error('Error:', response.statusText);
                    return false;
                }
            } catch (error) {
                this.error = error
            }
        }
    }
})

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
        async newGame(tablepresetId, rulesetId, player1Name, player2Name) {
            this.loading = true
            const data = {
                "ruleset_id": rulesetId,
                "table_id": tablepresetId,
                "player1_name": player1Name,
                "player2_name": player2Name
            }
            try {
                const response = await fetch('/api/game', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                })
                if (response.status === 200) {
                    return this.fetchGame();
                } else {
                    console.error('Error:', response.statusText);
                    console.log(response)
                    return false;
                }
            } catch (error) {
                console.error('Error:', error);
                return false;
            }
        }
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

        endTimer() {
            clearInterval(this.interval)
            this.interval = null;
            this.status = null;
            this.time = 60;
        },

        updateTime(time, status) {
            this.time = time;
            const oldStatus = this.status;

            if (oldStatus !== status) {
                this.status = status;
                if (status == 'paused') {
                    this.stopTimer();
                } else {
                    this.startTimer();
                }
            }
        }
    },
})