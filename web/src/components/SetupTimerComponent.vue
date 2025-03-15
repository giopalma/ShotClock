<script>
import { onMounted, ref } from 'vue'
import { useGameStore, useTimerStore } from '../store'
import Panel from 'primevue/panel'
import Button from 'primevue/button';
import { startGame, pauseGame, resumeGame } from '../api';

export default {
  components: {
    Panel, Button
  },
  setup() {
    const isGameCreated = ref(false)
    const currentIncrements = ref([0, 0])
    const currentPlayer = ref(0)
    const gameStatus = ref('paused')
    const playerNames = ref(['Player 1', 'Player 2'])
    const gameStore = useGameStore()
    const timerStore = useTimerStore()

    onMounted(async () => {
      await gameStore.fetchGame()
      const game = gameStore.game
      console.log(game)
      if (game !== null) {
        isGameCreated.value = true
        gameStatus.value = game.game_status
        currentPlayer.value = game.current_player
        playerNames.value = game.player_names
        currentIncrements.value = game.current_increments
      }
    })

    const incrementTime = () => {
      // Define the logic for incrementing time here
      console.log('Increment time clicked')
    }

    const cPauseResumeGame = async () => {
      if (gameStatus.value === 'running') {
        const success = await pauseGame()
        if (success) {
          gameStatus.value = 'paused'
          timerStore.stopTimer()
        }
      } else {
        const success = await resumeGame()
        if (success) {
          gameStatus.value = 'running'
          timerStore.startTimer()
        }
      }
    }

    const cNewGame = () => {
      // Define the logic for starting a new game here
      console.log('Start new game clicked')
    }

    const cStartGame = async () => {
      const success = await startGame()
      if (success) {
        timerStore.newTimer(60)
        timerStore.startTimer()
        gameStatus.value = 'running'
      }
    }

    return {
      isGameCreated,
      currentIncrements,
      currentPlayer,
      gameStatus,
      timerStore,
      playerNames,
      incrementTime,
      cPauseResumeGame,
      cNewGame,
      cStartGame
    }
  }
}
</script>

<template>
  <Panel header="Game Panel" id="game-panel">
    <div v-if="isGameCreated">
      <div class="time-display">
        <span>{{ timerStore.time !== null ? timerStore.time.toString().padStart(2, '0').slice(0, 2) : '--' }}</span>
      </div>
      <Button v-if="isGameCreated && gameStatus === 'ready'" @click="cStartGame" label="START" raised />
      <div class="buttons">
        <Button @click="cPauseResumeGame" :label="gameStatus === 'paused' ? 'RIPRENDI' : 'PAUSA'"
          :severity="gameStatus === 'paused' ? 'success' : 'warn'" />
        <Button :disabled="currentIncrements[currentPlayer] <= 0" @click="incrementTime" label="INCREMENTA TEMPO"
          severity="secondary" />
      </div>
    </div>
    <div v-else>
      <p>Nessun gioco avviato</p>
      <Button @click="cNewGame" label="AVVIA GIOCO" raised />
    </div>
  </Panel>
</template>
