<script setup>
import { ref, onMounted, computed } from 'vue'
import ButtonGroup from 'primevue/buttongroup'
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
  <Panel header="Game Panel" id="game-panel" class="w-full">
    <template v-if="isGameCreated">
      <div class="flex flex-col items-center">
        <span class="text-5xl font-bold m-4">
          {{
            timerStore.time !== null
              ? `${Math.floor(timerStore.time).toString().padStart(2, '0')}.${((timerStore.time % 1) *
                100).toFixed(0).padStart(2, '0')}`
              : '--.--'
          }}
        </span>

        <div class="flex flex-col w-full max-w-md">
          <ButtonGroup class="flex w-full">
            <Button v-if="gameStatus === 'ready'" @click="startGameHandler" label="START" class="flex-1" />
            <Button v-if="gameStatus !== 'ready'" @click="togglePauseResume"
              :label="gameStatus === 'paused' ? 'RIPRENDI' : 'PAUSA'"
              :severity="gameStatus === 'paused' ? 'success' : 'warn'" class="flex-1" />
            <Button label="TERMINA" @click="endGameHandler" severity="danger" class="flex-1" />
          </ButtonGroup>
          <div class="mb-2 text-center">
            <div class="font-bold mb-1">INCREMENTA TEMPO</div>
            <ButtonGroup class="flex w-full">
              <Button :disabled="currentIncrements[0] <= 0" @click="localIncrementTime(0)" :label="playerNames[0]"
                severity="secondary" class="flex-1" raised />
              <Button :disabled="currentIncrements[1] <= 0" @click="localIncrementTime(1)" :label="playerNames[1]"
                severity="secondary" class="flex-1" raised />
            </ButtonGroup>
          </div>
        </div>
      </div>
    </template>
    <template v-else>
      <div class="flex flex-col items-center">
        <p class="text-2xl font-bold m-4">Nessun gioco avviato</p>
        <Button @click="dialogVisible = true" label="AVVIA GIOCO" raised />
        <NewGameModal v-model:visible="dialogVisible" />
      </div>
    </template>
  </Panel>
</template>
