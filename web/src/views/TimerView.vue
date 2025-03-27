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

const integerTime = computed(() => Math.ceil(timerStore.time));

const mute = ref(true)
const alarmTriggered = ref(false)
const last_countdown_second = ref(6);
let audioCtx = null;

const playAlarmSound = (isFinal = false) => {
    const duration = isFinal ? 2 : 0.5;
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
        oscillator.stop(audioCtx.currentTime + duration);
    } catch (e) {
        console.error('Errore nella riproduzione audio:', e);
    }
}

// Gestisce l'allarme principale
const handleMainAlarm = (newTime) => {
    if (alarmTriggered.value && newTime > timerStore.allarmTime) {
        alarmTriggered.value = false;
    } else if (!alarmTriggered.value && newTime <= timerStore.allarmTime) {
        alarmTriggered.value = true;
        playAlarmSound();
    }
}

// Gestisce il conto alla rovescia finale
const handleCountdown = (newTime) => {
    const roundedTime = Math.ceil(newTime);
    if (roundedTime <= 5 && roundedTime >= 0 && roundedTime < last_countdown_second.value) {
        last_countdown_second.value = roundedTime;
        playAlarmSound(roundedTime === 0);
    }
}

watch(() => timerStore.time, (newTime) => {
    if (mute.value) return;

    handleMainAlarm(newTime);
    handleCountdown(newTime);
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
                    </div>
                </div>
            </template>
        </div>
    </div>
</template>
