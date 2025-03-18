<script setup>
import { watch, ref, nextTick, onUnmounted } from 'vue';
import { Dialog, Button, InputText, ButtonGroup } from 'primevue';
import { useSettingsStore } from '../store';
import { getFrameUrl, getFrameMaskedUrl } from '../api';

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
const imageRef = ref(null);           // Immagine attualmente visualizzata (mascherata o normale)
const originalImageRef = ref(null);   // Frame originale per operazioni sui punti
const listenersAttached = ref(false);
const points = ref([]); // Array di punti { x, y, type } in pixel
const draggingPoint = ref(null);
const name = ref("");

/**
 * Carica l'immagine e la disegna sul canvas.
 * Se storeOriginal è true, memorizza anche l'immagine originale.
 */
const loadImage = async (imageUrl, storeOriginal = false) => {
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

        if (storeOriginal) {
            originalImageRef.value = image;
        }
        imageRef.value = image;
        drawPoints(ctx); // Ridisegna eventuali punti presenti
    };
    image.onerror = (err) => {
        console.error("Errore nel caricamento dell'immagine:", err);
    };
    image.src = imageUrl;
};

const addColorPoint = () => {
    addPoint("color");
};

const addRecPoint = () => {
    addPoint("rect");
};

const addPoint = (point_type) => {
    if (!canvasRef.value || !imageRef.value) return;
    const canvas = canvasRef.value;
    // Aggiunge il nuovo punto al centro dell'immagine
    const newPoint = { x: canvas.width / 2, y: canvas.height / 2, type: point_type };
    points.value.push(newPoint);
    const ctx = canvas.getContext('2d');
    drawPoints(ctx);
};

const drawPoints = (ctx) => {
    if (!canvasRef.value || !imageRef.value) return;
    // Ridisegna l'immagine di sfondo (visualizzata mascherata)
    ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
    ctx.drawImage(imageRef.value, 0, 0, canvasRef.value.width, canvasRef.value.height);
    // Disegna ogni punto
    points.value.forEach((point) => {
        let color = point.type === "rect" ? "yellow" : "red";
        ctx.beginPath();
        ctx.arc(point.x, point.y, 8, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
        ctx.stroke();
    });
};

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
    points.value[draggingPoint.value].x = x;
    points.value[draggingPoint.value].y = y;
    const ctx = canvasRef.value.getContext('2d');
    drawPoints(ctx);
};

const stopDrag = () => {
    draggingPoint.value = null;
};

const handleContextMenu = (event) => {
    event.preventDefault();
    const { x, y } = getCanvasCoordinates(event);
    let removed = false;
    points.value = points.value.filter((point) => {
        const dx = x - point.x;
        const dy = y - point.y;
        if (!removed && Math.sqrt(dx * dx + dy * dy) < 10) {
            removed = true;
            return false;
        }
        return true;
    });
    const ctx = canvasRef.value.getContext('2d');
    drawPoints(ctx);
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

const reset = () => {
    canvasRef.value = null;
    containerRef.value = null;
    imageRef.value = null;
    originalImageRef.value = null;
    listenersAttached.value = false;
    points.value = [];
    draggingPoint.value = null;
    name.value = "";
};

watch(() => props.visible, async (v) => {
    if (v) {
        reset();
        const imageUrl = await getFrameUrl();
        // Carica l'immagine normale e la memorizza come originale
        loadImage(imageUrl, true);
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

/**
 * getPresetPoints utilizza originalImageRef per campionare i colori,
 * garantendo che i dati siano prelevati dal frame non mascherato.
 */
const getPresetPoints = () => {
    const offscreenCanvas = document.createElement('canvas', { willReadFrequently: true });
    offscreenCanvas.width = canvasRef.value.width;
    offscreenCanvas.height = canvasRef.value.height;
    const offscreenCtx = offscreenCanvas.getContext('2d');

    // Disegna l'immagine originale (non mascherata)
    offscreenCtx.drawImage(originalImageRef.value, 0, 0, offscreenCanvas.width, offscreenCanvas.height);

    const rgbToHex = (r, g, b) =>
        '#' +
        [r, g, b]
            .map((c) => {
                const hex = c.toString(16);
                return hex.length === 1 ? '0' + hex : hex;
            })
            .join('');

    const colors = [];
    const presetPoints = [];
    points.value.forEach((point) => {
        const x = Math.floor(point.x);
        const y = Math.floor(point.y);
        if (point.type == "color") {
            const pixelData = offscreenCtx.getImageData(x, y, 1, 1).data;
            const hexColor = rgbToHex(pixelData[0], pixelData[1], pixelData[2]);
            colors.push(hexColor);
        } else {
            presetPoints.push([x, y]);
        }

    });
    return {
        "colors": colors,
        "points": presetPoints
    };
};

/**
 * updateWithMask aggiorna il canvas con il frame mascherato,
 * ma i punti continueranno a utilizzare l'immagine originale.
 */
const updateWithMask = async () => {
    const data = getPresetPoints();
    const imageMaskedUrl = await getFrameMaskedUrl(data.points, data.colors);
    const imageUrl = await getFrameUrl()
    // Carica l'immagine mascherata senza aggiornare originalImageRef
    loadImage(imageUrl, true)
    loadImage(imageMaskedUrl, false);
};

const newTablePreset = async () => {
    if (!canvasRef.value || !imageRef.value || name.value.trim() === "") return;

    const data = getPresetPoints();
    console.log(data);
    settingsStore.addTablePreset(name.value.trim(), data.points, data.colors);
    closeDialog();
};
</script>

<template>
    <Dialog :visible="visible" @update:visible="emit('update:visible', $event)" modal header="Nuovo Table Preset"
        :style="{ width: '25rem' }">
        <span class="text-surface-500 dark:text-surface-400 block mb-8">
            Aggiungi una nuova configurazione per il tavolo da gioco.
        </span>
        <div class="flex items-center gap-4 mb-4">
            <label for="name" class="font-semibold w-24">Nome</label>
            <InputText type="text" v-model="name" class="flex-auto" :invalid="!name" />
        </div>
        <ButtonGroup>
            <Button @click="addColorPoint" severity="secondary" label="Colore" icon="pi pi-plus" size="small" />
            <Button @click="addRecPoint" severity="secondary" icon="pi pi-plus" label="Vertici" size="small" />
            <Button @click="updateWithMask" severity="secondary" icon="pi pi-refresh" label="Aggiorna" size="small" />
        </ButtonGroup>
        <div ref="containerRef" class="relative w-full mb-8">
            <canvas ref="canvasRef" class="absolute top-0 left-0 w-full h-full"></canvas>
        </div>
        <div class="flex justify-end gap-2">
            <Button type="button" label="Annulla" severity="secondary" @click="closeDialog"></Button>
            <Button type="button" label="Crea" @click="newTablePreset" :disabled="!name"></Button>
        </div>
    </Dialog>
</template>
