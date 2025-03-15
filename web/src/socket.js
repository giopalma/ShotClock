import { reactive } from "vue";
import { io } from "socket.io-client";
import { useGameStore, useTimerStore } from './store';

export const state = reactive({
    connected: false,
});

// "undefined" means the URL will be computed from the `window.location` object
const URL = "http://localhost:5000";

export const socket = io(URL);

socket.on("connect", () => {
    state.connected = true;
    console.log("Socket connected")
});

socket.on("disconnect", () => {
    state.connected = false;
});

socket.on("timer", (data) => {
    if (isNaN(data.timestamp) || isNaN(data.remaining_time)) {
        console.error("Received NaN data:", data);
        return;
    }

    const timerStore = useTimerStore();

    const timestamp = data.timestamp;
    const receivedTime = data.remaining_time;
    const status = data.status;
    const currentTimestamp = (Date.now() / 1000);
    const timeDifference = currentTimestamp - timestamp;
    const time = receivedTime - timeDifference;
    timerStore.updateTime(time, status);
});