<script setup>
import { ref, watch, nextTick, onUnmounted } from 'vue';
import interact from 'interactjs';
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
const imageRef = ref(null);           // Immagine visualizzata (mascherata o normale)
const originalImageRef = ref(null);   // Frame originale per operazioni sui punti
const points = ref([]); // Array di punti { x, y, type }
const draggingPoint = ref(null);
const name = ref("");

// Variabili per il cerchio
const circle = ref(null); // { x, y, radius }
const draggingCircle = ref(false);
const circleAreaThreshold = ref(100);
const circleAreaThresholdStep = 10;

const getCanvasCoordinates = (clientX, clientY) => {
    const canvas = canvasRef.value;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    return {
        x: (clientX - rect.left) * scaleX,
        y: (clientY - rect.top) * scaleY,
    };
};

const loadImage = async (imageUrl, storeOriginal = false) => {
    if (!imageUrl) {
        console.error("URL immagine non valido o errore nel recupero.");
        return;
    }
    const image = new Image();
    image.crossOrigin = "anonymous";
    image.onload = () => {
        if (!canvasRef.value || !containerRef.value) return;
        const canvas = canvasRef.value;
        const container = containerRef.value;
        const ctx = canvas.getContext('2d');
        const aspectRatio = image.width / image.height;
        container.style.paddingBottom = `${100 / aspectRatio}%`;
        canvas.width = image.width;
        canvas.height = image.height;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
        if (storeOriginal) {
            originalImageRef.value = image;
        }
        imageRef.value = image;
        drawAll(ctx);
    };
    image.onerror = (err) => {
        console.error("Errore nel caricamento dell'immagine:", err);
    };
    image.src = imageUrl;
};

const drawAll = (ctx) => {
    if (!canvasRef.value || !imageRef.value) return;
    ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
    ctx.drawImage(imageRef.value, 0, 0, canvasRef.value.width, canvasRef.value.height);
    points.value.forEach((point) => {
        const size = 5;
        // Disegna il bordo nero
        ctx.beginPath();
        ctx.moveTo(point.x - size, point.y);
        ctx.lineTo(point.x + size, point.y);
        ctx.moveTo(point.x, point.y - size);
        ctx.lineTo(point.x, point.y + size);
        ctx.lineWidth = 4;
        ctx.strokeStyle = "black";
        ctx.stroke();

        // Disegna il simbolo "+" nel colore specifico
        ctx.beginPath();
        ctx.moveTo(point.x - size, point.y);
        ctx.lineTo(point.x + size, point.y);
        ctx.moveTo(point.x, point.y - size);
        ctx.lineTo(point.x, point.y + size);
        ctx.lineWidth = 2;
        ctx.strokeStyle = point.type === "rect" ? "yellow" : "red";
        ctx.stroke();
    });
    if (circle.value) {
        ctx.beginPath();
        ctx.arc(circle.value.x, circle.value.y, circle.value.radius, 0, Math.PI * 2);
        ctx.strokeStyle = "red";
        ctx.lineWidth = 1;
        ctx.stroke();
    }
};

const addPoint = (point_type) => {
    if (!canvasRef.value || !imageRef.value) return;
    const canvas = canvasRef.value;
    const newPoint = { x: canvas.width / 2, y: canvas.height / 2, type: point_type };
    points.value.push(newPoint);
    const ctx = canvas.getContext('2d');
    drawAll(ctx);
};

const addColorPoint = () => addPoint("color");
const addRecPoint = () => addPoint("rect");

const addCircle = () => {
    if (!canvasRef.value || !imageRef.value) return;
    if (circle.value) return;
    const canvas = canvasRef.value;
    circle.value = {
        x: canvas.width / 2,
        y: canvas.height / 2,
        radius: Math.sqrt(circleAreaThreshold.value / Math.PI)
    };
    const ctx = canvas.getContext('2d');
    drawAll(ctx);
};

const increaseCircleArea = () => {
    if (!circle.value) return;
    circleAreaThreshold.value += circleAreaThresholdStep;
    circle.value.radius = Math.sqrt(circleAreaThreshold.value / Math.PI);
    const ctx = canvasRef.value.getContext('2d');
    drawAll(ctx);
};

const decreaseCircleArea = () => {
    if (!circle.value || circleAreaThreshold.value <= circleAreaThresholdStep) return;
    circleAreaThreshold.value -= circleAreaThresholdStep;
    circle.value.radius = Math.sqrt(circleAreaThreshold.value / Math.PI);
    const ctx = canvasRef.value.getContext('2d');
    drawAll(ctx);
};

const reset = () => {
    imageRef.value = null;
    originalImageRef.value = null;
    points.value = [];
    draggingPoint.value = null;
    name.value = "";
    circle.value = null;
    draggingCircle.value = false;
    circleAreaThreshold.value = 100;
};

const getPresetPoints = () => {
    const offscreenCanvas = document.createElement('canvas', { willReadFrequently: true });
    offscreenCanvas.width = canvasRef.value.width;
    offscreenCanvas.height = canvasRef.value.height;
    const offscreenCtx = offscreenCanvas.getContext('2d');
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
        if (point.type === "color") {
            const pixelData = offscreenCtx.getImageData(x, y, 1, 1).data;
            colors.push(rgbToHex(pixelData[0], pixelData[1], pixelData[2]));
        } else {
            presetPoints.push([x, y]);
        }
    });
    return {
        colors,
        points: presetPoints
    };
};

const updateWithMask = async () => {
    const data = getPresetPoints();
    const imageMaskedUrl = await getFrameMaskedUrl(data.points, data.colors);
    const imageUrl = await getFrameUrl();
    // Aggiorno entrambe le immagini: quella originale e quella mascherata
    loadImage(imageUrl, true);
    loadImage(imageMaskedUrl, false);
};

const newTablePreset = async () => {
    if (!canvasRef.value || !imageRef.value || name.value.trim() === "") return;
    const data = getPresetPoints();
    const circleThreshold = circle.value ? Math.round(circleAreaThreshold.value / 2) : 50;
    settingsStore.addTablePreset(name.value.trim(), data.points, data.colors, circleThreshold);
    closeDialog();
};

// Variabili per il drag tramite Interact.js
let dragMode = null; // "circle" oppure "point"

const dragStart = (event) => {
    const { x, y } = getCanvasCoordinates(event.clientX, event.clientY);
    // Controllo il cerchio
    if (circle.value) {
        const dx = x - circle.value.x;
        const dy = y - circle.value.y;
        if (Math.sqrt(dx * dx + dy * dy) < circle.value.radius) {
            dragMode = "circle";
            draggingCircle.value = true;
            return;
        }
    }
    // Controllo i punti
    for (let i = 0; i < points.value.length; i++) {
        const point = points.value[i];
        const dx = x - point.x;
        const dy = y - point.y;
        if (Math.sqrt(dx * dx + dy * dy) < 10) {
            dragMode = "point";
            draggingPoint.value = i;
            return;
        }
    }
    dragMode = null;
};

const dragMove = (event) => {
    if (!dragMode) return;
    if (event.originalEvent) event.originalEvent.preventDefault();
    const { x, y } = getCanvasCoordinates(event.clientX, event.clientY);
    if (dragMode === "circle" && circle.value) {
        circle.value.x = x;
        circle.value.y = y;
    } else if (dragMode === "point" && draggingPoint.value !== null) {
        points.value[draggingPoint.value].x = x;
        points.value[draggingPoint.value].y = y;
    }
    const ctx = canvasRef.value.getContext('2d');
    drawAll(ctx);
};

const dragEnd = () => {
    dragMode = null;
    draggingPoint.value = null;
    draggingCircle.value = false;
};

const removePointAt = (x, y) => {
    for (let i = 0; i < points.value.length; i++) {
        const point = points.value[i];
        const dx = x - point.x;
        const dy = y - point.y;
        if (Math.sqrt(dx * dx + dy * dy) < 10) {
            points.value.splice(i, 1);
            const ctx = canvasRef.value.getContext('2d');
            drawAll(ctx);
            break;
        }
    }
};

const initInteract = () => {
    if (!canvasRef.value) return;
    interact(canvasRef.value).draggable({
        listeners: {
            start(event) {
                dragStart(event);
            },
            move(event) {
                dragMove(event);
            },
            end(event) {
                dragEnd(event);
            }
        }
    });
    canvasRef.value.addEventListener('dblclick', (event) => {
        const { x, y } = getCanvasCoordinates(event.clientX, event.clientY);
        removePointAt(x, y);
    });
};

watch(() => props.visible, async (v) => {
    if (v) {
        reset();
        const imageUrl = await getFrameUrl();
        loadImage(imageUrl, true);
        await nextTick();
        initInteract();
    }
});

onUnmounted(() => {
    if (canvasRef.value) {
        interact(canvasRef.value).unset();
    }
});
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
            <canvas ref="canvasRef" class="absolute top-0 left-0 w-full h-full" style="touch-action: none;"></canvas>
        </div>
        <div class="flex justify-end gap-2">
            <Button type="button" label="Annulla" severity="secondary" @click="closeDialog"></Button>
            <Button type="button" label="Crea" @click="newTablePreset" :disabled="!name"></Button>
        </div>
    </Dialog>
</template>