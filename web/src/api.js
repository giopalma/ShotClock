import { useGameStore, useTimerStore } from "./store";

async function gameAction(action) {
    const formData = new FormData();
    formData.append('action', action);

    try {
        const response = await fetch('/api/game/actions', {
            method: 'POST',
            body: formData
        });

        if (response.status === 200) {
            return true;
        } else {
            console.error('Error:', response.statusText);
            return false;
        }
    } catch (error) {
        console.error('Error:', error);
        return false;
    }
}

export async function startGame() {
    return gameAction('start');
}


export async function pauseGame() {
    return gameAction('pause');
}

export async function resumeGame() {
    return gameAction('resume');
}

export async function endGame() {
    const result = gameAction('end');
    useGameStore().fetchGame()
    useTimerStore().endTimer()
    return result
}

export async function getFrameUrl() {
    try {
        const response = await fetch('/api/video/frame');
        if (!response.ok) {
            throw new Error(`Errore HTTP! Stato: ${response.status}`);
        }

        const blob = await response.blob(); // Qui era l'errore
        return URL.createObjectURL(blob);
    } catch (error) {
        console.error("Errore durante il recupero del frame:", error);
        return null; // Restituisci null in caso di errore
    }
}