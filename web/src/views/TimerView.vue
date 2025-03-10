<script setup>
import { ref, watchEffect } from 'vue'
const loading = ref(true);
const error = ref(null);
const game = ref(null);

async function fetchGame() {
    try {
        const response = await fetch('/api/game');
        const _game = await response.json();
        game.value = _game;
    } catch (e) {
        error.value = e.toString();
    } finally {
        loading.value = false;
    }
}
watchEffect(() => {fetchGame()});
</script>

<template>
    <div v-if="loading"><p>Caricamento...</p></div>
    <div v-if="error"><p>Errore: {{ error }}</p></div>
    <div v-else>
        <h1>Timer</h1>
        <p>Tempo rimanente: {{ game.time }}</p>
    </div>
</template>

<style scoped>
</style>
