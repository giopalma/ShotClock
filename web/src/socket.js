import { reactive } from "vue";
import { io } from "socket.io-client";
import { useGameStore, useTimerStore } from './store';

export const state = reactive({
    connected: false,
    timeOffset: 0,
});

export const socket = io('', {
    path: '/socket.io',
    transports: ['websocket', 'polling'],
    reconnection: true,
    reconnectionAttempts: Infinity,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    timeout: 20000,
    autoConnect: true,
    forceNew: true
});

socket.on("connect", () => {
    state.connected = true;
    console.log("Socket connected");
});


socket.on("time_sync", (data) => {
    const clientTime = Date.now() / 1000;
    state.timeOffset = data.server_time - clientTime;
    console.log("Time offset:", state.timeOffset);
});

socket.on("disconnect", () => {
    state.connected = false;
    console.log("Socket disconnected");
});

socket.on("connect_error", (error) => {
    console.error("Errore di connessione Socket.IO:", error);
});

socket.on("error", (error) => {
    console.error("Errore Socket.IO:", error);
});

socket.on("reconnect_attempt", (attemptNumber) => {
    console.log("Tentativo di riconnessione:", attemptNumber);
});

socket.on("reconnect", () => {
    console.log("Socket riconnesso");
});

socket.on("game", async (data) => {
    const timerStore = useTimerStore()
    const gameStore = useGameStore()
    console.log("Websocket Game: " + data)
    if (data === "created" || data === "ended") {
        await gameStore.fetchGame()
        timerStore.endTimer()
    }
    if (data === "created") {
        timerStore.newTimer()
    }
    console.log(gameStore.game)
})

socket.on("timer", (data) => {
    if (isNaN(data.timestamp) || isNaN(data.remaining_time)) {
        console.error("Received NaN data:", data);
        return;
    }

    const timerStore = useTimerStore();
    console.log("Device timestamp: " + data.timestamp)
    console.log("Device remaining time: " + data.remaining_time)

    const timestamp = data.timestamp;
    const receivedTime = data.remaining_time;
    const status = data.status;
    const currentTimestamp = (Date.now() / 1000) + state.timeOffset; // Aggiungiamo l'offset
    console.log("Front-end Timestamp (with offset): " + currentTimestamp)

    const timeDifference = Math.max(0, currentTimestamp - timestamp);
    let time = Math.max(0, receivedTime - timeDifference);

    timerStore.updateTime(time, status);
});