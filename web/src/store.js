import { defineStore } from 'pinia'

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
            console.log("Fetching game")
            this.loading = true;
            try {
                const response = await fetch('/api/game');
                const body = await response.json();
                if (body.message == 'No game in progress') {
                    this.game = null;
                    this.error = 'No game in progress';
                } else {
                    this.game = body;
                    console.log("GIOCO FETCHATO")
                    console.log(this.game)
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
                    console.log("New Game created")
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
        time: 60.00,
        allarmTime: 10,
        interval: null,
        status: null,
    }),

    actions: {
        async newTimer() {
            const gameStore = useGameStore();
            const settingsStore = useSettingsStore();
            await gameStore.fetchGame()
            await settingsStore.fetchTablePresetsRulesets()
            console.log("GameStore:")
            console.log(gameStore.game)
            if (gameStore.game && gameStore.game.ruleset_id) {
                console.log("Received ruleset_id: " + gameStore.game.ruleset_id)
                const ruleset = settingsStore.rulesets.find(ruleset => ruleset.id === gameStore.game.ruleset_id);
                console.log(ruleset)
                this.time = ruleset.initial_duration;
                this.allarmTime = ruleset.allarm_time;
            }
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