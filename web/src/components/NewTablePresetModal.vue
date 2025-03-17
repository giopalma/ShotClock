<script setup>
import { watch, ref, nextTick, onUnmounted } from 'vue';
import { Dialog, Button, InputText } from 'primevue';
import { useSettingsStore } from '../store';
import { getFrameUrl } from '../api';

const settingsStore = useSettingsStore();
const props = defineProps({
    visible: Boolean
});
const emit = defineEmits(['update:visible']);

const closeDialog = () => {
    emit('update:visible', false);
};

const canvasRef = ref(null);
const containerRef = ref(null);
const imageRef = ref(null); // Memorizza l'immagine
const listenersAttached = ref(false);

const loadImage = async () => {
    const imageUrl = await getFrameUrl();
    if (!imageUrl) {
        console.error("URL immagine non valido o errore nel recupero.");
        return;
    }
    console.log("Caricamento immagine da:", imageUrl);
    const image = new Image();
    image.crossOrigin = "anonymous"; // Se necessario
    image.onload = () => {
        if (!canvasRef.value || !containerRef.value) return;
        const canvas = canvasRef.value;
        const container = containerRef.value;
        const ctx = canvas.getContext('2d');

        // Calcola l'aspect ratio e imposta il padding del container
        const aspectRatio = image.width / image.height;
        container.style.paddingBottom = `${100 / aspectRatio}%`;

        // Imposta le dimensioni interne del canvas in base all'immagine
        canvas.width = image.width;
        canvas.height = image.height;

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(image, 0, 0, canvas.width, canvas.height);

        imageRef.value = image;
        drawColorPoints(ctx); // Ridisegna eventuali punti presenti
    };
    image.onerror = (err) => {
        console.error("Errore nel caricamento dell'immagine:", err);
    };
    image.src = imageUrl;
};

const points = ref([]); // Array di punti { x, y } in pixel dell'immagine
const draggingPoint = ref(null);

const addColorPoint = () => {
    if (!canvasRef.value || !imageRef.value) return;
    const canvas = canvasRef.value;
    // Aggiunge il nuovo punto al centro dell'immagine
    const newPoint = { x: canvas.width / 2, y: canvas.height / 2 };
    points.value.push(newPoint);
    const ctx = canvas.getContext('2d');
    drawColorPoints(ctx);
};

const drawColorPoints = (ctx) => {
    if (!canvasRef.value || !imageRef.value) return;
    // Ridisegna l'immagine di sfondo
    ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
    ctx.drawImage(imageRef.value, 0, 0, canvasRef.value.width, canvasRef.value.height);
    // Disegna ogni punto
    points.value.forEach((point) => {
        ctx.beginPath();
        ctx.arc(point.x, point.y, 8, 0, Math.PI * 2);
        ctx.fillStyle = "red";
        ctx.fill();
        ctx.stroke();
    });
};

// Calcola le coordinate interne del canvas (in pixel dell'immagine)
const getCanvasCoordinates = (event) => {
    const canvas = canvasRef.value;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    return {
        x: (event.clientX - rect.left) * scaleX,
        y: (event.clientY - rect.top) * scaleY,
    };
};

const startDrag = (event) => {
    if (!canvasRef.value) return;
    const { x, y } = getCanvasCoordinates(event);
    points.value.forEach((point, index) => {
        const dx = x - point.x;
        const dy = y - point.y;
        if (Math.sqrt(dx * dx + dy * dy) < 10) {
            draggingPoint.value = index;
        }
    });
};

const drag = (event) => {
    if (draggingPoint.value === null || !canvasRef.value) return;
    const { x, y } = getCanvasCoordinates(event);
    points.value[draggingPoint.value] = { x, y };
    const ctx = canvasRef.value.getContext('2d');
    drawColorPoints(ctx);
};

const stopDrag = () => {
    draggingPoint.value = null;
};

// Gestione del clic destro per rimuovere il punto
const handleContextMenu = (event) => {
    event.preventDefault(); // Impedisce l'apertura del menu contestuale
    const { x, y } = getCanvasCoordinates(event);
    let removed = false;
    // Filtra i punti rimuovendo quello cliccato
    points.value = points.value.filter((point) => {
        const dx = x - point.x;
        const dy = y - point.y;
        if (!removed && Math.sqrt(dx * dx + dy * dy) < 10) {
            removed = true;
            return false; // Rimuove il punto
        }
        return true;
    });
    const ctx = canvasRef.value.getContext('2d');
    drawColorPoints(ctx);
};

const attachCanvasListeners = () => {
    const canvas = canvasRef.value;
    if (canvas && !listenersAttached.value) {
        canvas.addEventListener("mousedown", startDrag);
        canvas.addEventListener("mousemove", drag);
        canvas.addEventListener("mouseup", stopDrag);
        canvas.addEventListener("mouseleave", stopDrag);
        canvas.addEventListener("contextmenu", handleContextMenu);
        listenersAttached.value = true;
    }
};

const removeCanvasListeners = () => {
    const canvas = canvasRef.value;
    if (canvas && listenersAttached.value) {
        canvas.removeEventListener("mousedown", startDrag);
        canvas.removeEventListener("mousemove", drag);
        canvas.removeEventListener("mouseup", stopDrag);
        canvas.removeEventListener("mouseleave", stopDrag);
        canvas.removeEventListener("contextmenu", handleContextMenu);
        listenersAttached.value = false;
    }
};

watch(() => props.visible, (v) => {
    if (v) {
        loadImage();
        nextTick(() => {
            attachCanvasListeners();
        });
    } else {
        removeCanvasListeners();
    }
});

onUnmounted(() => {
    removeCanvasListeners();
});

const newTablePreset = async () => {
    if (!canvasRef.value || !imageRef.value) return;

    // Crea un canvas offscreen con l'attributo willReadFrequently per migliorare le performance
    const offscreenCanvas = document.createElement('canvas', { willReadFrequently: true });
    offscreenCanvas.width = canvasRef.value.width;
    offscreenCanvas.height = canvasRef.value.height;
    const offscreenCtx = offscreenCanvas.getContext('2d');

    // Disegna l'immagine originale sul canvas offscreen
    offscreenCtx.drawImage(imageRef.value, 0, 0, offscreenCanvas.width, offscreenCanvas.height);

    // Funzione helper per convertire RGB in HEX
    const rgbToHex = (r, g, b) =>
        '#' +
        [r, g, b]
            .map((c) => {
                const hex = c.toString(16);
                return hex.length === 1 ? '0' + hex : hex;
            })
            .join('');

    // Per ogni punto, ottieni le coordinate (in pixel dell'immagine) e il colore corrispondente
    const presetPoints = points.value.map((point) => {
        const x = Math.floor(point.x);
        const y = Math.floor(point.y);
        const pixelData = offscreenCtx.getImageData(x, y, 1, 1).data; // [r, g, b, a]
        const hexColor = rgbToHex(pixelData[0], pixelData[1], pixelData[2]);
        return { x, y, color: hexColor };
    });

    console.log("Preset points with color:", presetPoints);
    // Qui puoi procedere con ulteriori logiche (salvataggio, invio, ecc.) usando presetPoints
};

const name = ref("");
</script>

<template>
    <Dialog :visible="visible" @update:visible="emit('update:visible', $event)" modal header="Nuovo Table Preset"
        :style="{ width: '25rem' }">
        <span class="text-surface-500 dark:text-surface-400 block mb-8">
            Aggiungi una nuova configurazione per il tavolo da gioco.
        </span>
        <div class="flex items-center gap-4 mb-4">
            <label for="tableprest" class="font-semibold w-24">Nome</label>
            <InputText type="text" v-model="name" class="flex-auto" />
        </div>
        <div ref="containerRef" class="relative w-full mb-8">
            <canvas ref="canvasRef" class="absolute top-0 left-0 w-full h-full"></canvas>
            <button @click="addColorPoint"
                class="absolute top-2 right-2 bg-blue-500 text-white p-2 rounded-full text-xs shadow-lg">
                +
            </button>
        </div>
        <div class="flex justify-end gap-2">
            <Button type="button" label="Annulla" severity="secondary" @click="closeDialog"></Button>
            <Button type="button" label="Crea" @click="newTablePreset"></Button>
        </div>
    </Dialog>
</template>
