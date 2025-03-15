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