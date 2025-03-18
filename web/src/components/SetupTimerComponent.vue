<script setup>
import { ref, onMounted, computed } from 'vue'
import Panel from 'primevue/panel'
import Button from 'primevue/button'
import NewGameModal from './NewGameModal.vue'
import { useGameStore, useTimerStore } from '../store'
import { startGame, pauseGame, resumeGame, endGame, incrementTime } from '../api'

// Stato locale
const dialogVisible = ref(false)

// Store di gioco e timer
const gameStore = useGameStore()
const timerStore = useTimerStore()

// Computed properties per monitorare lo stato dello store
const isGameCreated = computed(() => gameStore.game !== null)
const gameStatus = computed(() => gameStore.game ? gameStore.game.game_status : 'paused')
const playerNames = computed(() => gameStore.game ? gameStore.game.player_names : ['Player 1', 'Player 2'])
const currentIncrements = computed(() => gameStore.game ? gameStore.game.current_increments : [0, 0])

// Carica il gioco al montaggio del componente
onMounted(async () => {
  await gameStore.fetchGame()
})

// Logica per l'incremento del tempo
const localIncrementTime = (player) => {
  incrementTime(player)
}

// Alterna pausa/ripresa del gioco
const togglePauseResume = async () => {
  if (gameStatus.value === 'running') {
    if (await pauseGame()) {
      gameStore.game.game_status = 'paused'
      timerStore.stopTimer()
    }
  } else {
    if (await resumeGame()) {
      gameStore.game.game_status = 'running'
      timerStore.startTimer()
    }
  }
}

// Avvio del gioco
const startGameHandler = async () => {
  if (await startGame()) {
    timerStore.newTimer(60)
    timerStore.startTimer()
    gameStore.game.game_status = 'running'
  }
}

const endGameHandler = async () => {
  await endGame()
}
</script>

<template>
  <Panel header="Game Panel" id="game-panel">
    <template v-if="isGameCreated">
      <div class="time-display">
        <span>
          {{
            timerStore.time !== null
              ? timerStore.time.toString().padStart(2, '0').slice(0, 2)
              : '--'
          }}
        </span>
      </div>
      <Button v-if="gameStatus === 'ready'" @click="startGameHandler" label="START" raised />
      <div class="buttons">
        <Button @click="togglePauseResume" :label="gameStatus === 'paused' ? 'RIPRENDI' : 'PAUSA'"
          :severity="gameStatus === 'paused' ? 'success' : 'warn'" />
        <Button :disabled="currentIncrements[0] <= 0" @click="localIncrementTime(0)"
          :label="`INCREMENTA TEMPO ${playerNames[0]}`" severity="secondary" />
        <Button :disabled="currentIncrements[1] <= 0" @click="localIncrementTime(1)"
          :label="`INCREMENTA TEMPO ${playerNames[1]}`" severity="secondary" />
        <Button label="TERMINA" raised @click="endGameHandler" severity="danger" />
      </div>
    </template>
    <template v-else>
      <p>Nessun gioco avviato</p>
      <Button @click="dialogVisible = true" label="AVVIA GIOCO" raised />
      <NewGameModal v-model:visible="dialogVisible" />
    </template>
  </Panel>
</template>
