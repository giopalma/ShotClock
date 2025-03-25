<script setup>
import { computed, onMounted } from 'vue';
import { useTimerStore } from '../store';
import { useGameStore } from '../store';

const gameStore = useGameStore();
const timerStore = useTimerStore();

onMounted(async () => {
    await gameStore.fetchGame()
    await timerStore.newTimer()
})

const integerTime = computed(() => Math.floor(timerStore.time));
const decimalTime = computed(() => {
    const fractional = timerStore.time - Math.floor(timerStore.time);
    return fractional.toFixed(2).substring(1);
});
</script>

<template>
    <template v-if="!gameStore.game">
        <span>Nessun gioco in corso</span>
    </template>
    <template v-else>
        <div class="flex items-center justify-center h-screen w-screen overflow-hidden">
            <div class="text-center w-full">
                <span class="text-[10rem] md:text-[25rem] lg:text-[30rem] font-bold">{{ integerTime }}</span>
                <span class="text-[4rem] md:text-[10rem] lg:text-[12rem] ml-1 align-[super]">{{ decimalTime }}</span>
            </div>
        </div>
    </template>
</template>
