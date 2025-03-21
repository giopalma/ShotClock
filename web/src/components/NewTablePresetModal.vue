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

// Aggiungo variabili per il cerchio
const circle = ref(null); // {x, y, radius}
const draggingCircle = ref(false);
const resizingCircle = ref(false);
const circleAreaThreshold = ref(100); // Valore predefinito per l'area del cerchio

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
        drawAll(ctx); // Ridisegna eventuali punti presenti
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

// Aggiungi la funzione per creare un cerchio
const addCircle = () => {
    if (!canvasRef.value || !imageRef.value) return;
    const canvas = canvasRef.value;

    // Se esiste già un cerchio, non faccio nulla
    if (circle.value) return;

    // Creo il cerchio al centro del canvas
    circle.value = {
        x: canvas.width / 2,
        y: canvas.height / 2,
        radius: Math.sqrt(circleAreaThreshold.value / Math.PI)  // Calcolo il raggio dall'area
    };

    const ctx = canvas.getContext('2d');
    drawAll(ctx);
};

const circleAreaThresholdStep = 10;
// Funzione per aumentare l'area del cerchio
const increaseCircleArea = () => {
    if (!circle.value) return;
    circleAreaThreshold.value += circleAreaThresholdStep;
    circle.value.radius = Math.sqrt(circleAreaThreshold.value / Math.PI);
    const ctx = canvasRef.value.getContext('2d');
    drawAll(ctx);
};

// Funzione per diminuire l'area del cerchio
const decreaseCircleArea = () => {
    if (!circle.value || circleAreaThreshold.value <= circleAreaThresholdStep) return;
    circleAreaThreshold.value -= circleAreaThresholdStep;
    circle.value.radius = Math.sqrt(circleAreaThreshold.value / Math.PI);
    const ctx = canvasRef.value.getContext('2d');
    drawAll(ctx);
};

const addPoint = (point_type) => {
    if (!canvasRef.value || !imageRef.value) return;
    const canvas = canvasRef.value;
    // Aggiunge il nuovo punto al centro dell'immagine
    const newPoint = { x: canvas.width / 2, y: canvas.height / 2, type: point_type };
    points.value.push(newPoint);
    const ctx = canvas.getContext('2d');
    drawAll(ctx);
};

const drawAll = (ctx) => {
    if (!canvasRef.value || !imageRef.value) return;
    // Ridisegna l'immagine di sfondo
    ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
    ctx.drawImage(imageRef.value, 0, 0, canvasRef.value.width, canvasRef.value.height);

    // Disegna ogni punto
    points.value.forEach((point) => {
        let color = point.type === "rect" ? "yellow" : "red";
        ctx.beginPath();
        ctx.arc(point.x, point.y, 5, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.fill();
        ctx.stroke();
    });

    // Disegna il cerchio se esiste
    if (circle.value) {
        ctx.beginPath();
        ctx.arc(circle.value.x, circle.value.y, circle.value.radius, 0, Math.PI * 2);
        ctx.strokeStyle = "red";
        ctx.lineWidth = 1;
        ctx.stroke();
    }
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

    // Verifica se si sta cliccando sul cerchio
    if (circle.value) {
        const dx = x - circle.value.x;
        const dy = y - circle.value.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        // Verifica se si sta cliccando all'interno per spostare
        if (distance < circle.value.radius) {
            draggingCircle.value = true;
            return;
        }
    }

    // Altrimenti, verifica se si sta cliccando su un punto esistente
    points.value.forEach((point, index) => {
        const dx = x - point.x;
        const dy = y - point.y;
        if (Math.sqrt(dx * dx + dy * dy) < 10) {
            draggingPoint.value = index;
        }
    });
};

const drag = (event) => {
    if (!canvasRef.value) return;
    const { x, y } = getCanvasCoordinates(event);
    const ctx = canvasRef.value.getContext('2d');

    // Gestisci il trascinamento del cerchio
    if (draggingCircle.value && circle.value) {
        circle.value.x = x;
        circle.value.y = y;
        drawAll(ctx);
        return;
    }

    // Gestisci il trascinamento di un punto esistente
    if (draggingPoint.value !== null) {
        points.value[draggingPoint.value].x = x;
        points.value[draggingPoint.value].y = y;
        drawAll(ctx);
    }
};

const stopDrag = () => {
    draggingPoint.value = null;
    draggingCircle.value = false;
};

const handleContextMenu = (event) => {
    event.preventDefault();
    const { x, y } = getCanvasCoordinates(event);

    // Verifica se si sta facendo clic destro sul cerchio
    if (circle.value) {
        const dx = x - circle.value.x;
        const dy = y - circle.value.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < circle.value.radius || Math.abs(distance - circle.value.radius) < 10) {
            circle.value = null; // Rimuove il cerchio
            const ctx = canvasRef.value.getContext('2d');
            drawAll(ctx);
            return;
        }
    }

    // Gestione per i punti esistenti
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
    drawAll(ctx);
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
    circle.value = null;
    draggingCircle.value = false;
    resizingCircle.value = false;
    circleAreaThreshold.value = 100;
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
    // Aggiungo il valore della soglia dell'area del cerchio ai dati (dimezzato)
    const circleThreshold = circle.value ? Math.round(circleAreaThreshold.value / 2) : 50;
    console.log(data);
    settingsStore.addTablePreset(name.value.trim(), data.points, data.colors, circleThreshold);
    closeDialog();
};
</script>

<template>
    <Dialog :visible="visible" @update:visible="emit('update:visible', $event)" modal header="Nuovo Table Preset"
        :style="{ width: '50rem' }">
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
            <Button @click="addCircle" severity="secondary" icon="pi pi-plus" label="Cerchio" size="small" />
            <Button @click="updateWithMask" severity="secondary" icon="pi pi-refresh" label="Aggiorna" size="small" />
        </ButtonGroup>

        <!-- Controlli per il cerchio -->
        <div v-if="circle" class="flex items-center gap-2 my-2">
            <label class="text-sm">Area cerchio: {{ circleAreaThreshold }}</label>
            <ButtonGroup>
                <Button @click="decreaseCircleArea" icon="pi pi-minus" size="small" />
                <Button @click="increaseCircleArea" icon="pi pi-plus" size="small" />
            </ButtonGroup>
        </div>

        <div ref="containerRef" class="relative w-full mb-8" style="transform: scale(1); transform-origin: top left">
            <canvas ref="canvasRef" class="absolute top-0 left-0 w-full h-full"></canvas>
        </div>
        <div class="flex justify-end gap-2">
            <Button type="button" label="Annulla" severity="secondary" @click="closeDialog"></Button>
            <Button type="button" label="Crea" @click="newTablePreset" :disabled="!name"></Button>
        </div>
    </Dialog>
</template>
