async function getCurrentTimer() {
    const response = await fetch('/api/timer');
    return response.json();
}