<script setup>
import { computed, onMounted, watch } from 'vue';
import { useTimerStore } from '../store';
import { useGameStore } from '../store';
import { ref } from 'vue';
import { Button } from 'primevue';

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

const mute = ref(true)
const allarmed = ref(false)
let audioCtx = null;

const playAlarmSound = () => {
    try {
        if (!audioCtx) {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
        const oscillator = audioCtx.createOscillator();
        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(1000, audioCtx.currentTime);
        const gainNode = audioCtx.createGain();
        gainNode.gain.value = 0.5;
        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);
        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 0.5);
    } catch (e) {
        console.error('Errore nella riproduzione audio:', e);
    }
}

watch(() => timerStore.time, (newTime) => {
    if (!mute.value) {
        if (allarmed.value && newTime > timerStore.allarmTime) {
            allarmed.value = false;
        }
        if (!allarmed.value && newTime <= timerStore.allarmTime && !mute.value) {
            allarmed.value = true;
            console.log("Allarm");
            playAlarmSound();
        }
    }
});
</script>

<template>
    <div class="relative min-h-screen p-4">
        <div class="absolute top-4 right-4 z-10">
            <Button text rounded aria-label="mute" :icon="mute ? 'pi pi-bell-slash' : 'pi pi-bell'"
                @click="mute = !mute" :label="mute ? 'ATTIVA L\'AUDIO' : 'DISATTIVA L\'AUDIO'" />
        </div>

        <div class="h-full">
            <template v-if="!gameStore.game">
                <span class="text-center text-xl">Nessun gioco in corso</span>
            </template>
            <template v-else>
                <div class="flex items-center justify-center h-screen w-screen overflow-hidden">
                    <div class="text-center w-full">
                        <span class="text-[10rem] md:text-[25rem] lg:text-[30rem] font-bold">{{ integerTime }}</span>
                        <span class="text-[4rem] md:text-[10rem] lg:text-[12rem] ml-1 align-[super]">{{ decimalTime
                            }}</span>
                    </div>
                </div>
            </template>
        </div>
    </div>
</template>
