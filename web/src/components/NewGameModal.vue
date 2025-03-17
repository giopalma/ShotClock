<script setup>
import { watch, ref } from 'vue';
import { Dialog, Select, Button, InputText, Divider } from 'primevue';
import { useGameStore, useSettingsStore } from '../store';

const settingsStore = useSettingsStore();
const gameStore = useGameStore();
const props = defineProps({
    visible: Boolean
});

const emit = defineEmits(['update:visible']);

const closeDialog = () => {
    emit('update:visible', false);
};

const newGame = async () => {
    gameStore.newGame(selectedTablePreset.value.id, selectedRuleset.value.id, player1Name.value, player2Name.value);
    closeDialog()
};

watch(() => props.visible, (v) => {
    if (v) {
        settingsStore.fetchTablePresetsRulesets();
    }
});

const player1Name = ref("Nome giocatore 1");
const player2Name = ref("Nome giocatore 2");
const selectedTablePreset = ref(null);
const selectedRuleset = ref(null);
</script>

<template>
    <Dialog :visible="visible" @update:visible="emit('update:visible', $event)" modal header="Nuovo Gioco"
        :style="{ width: '25rem' }">
        <span class="text-surface-500 dark:text-surface-400 block mb-8">
            Imposta le configurazioni per il nuovo gioco.
        </span>
        <div class="flex items-center gap-4 mb-4">
            <label for="tableprest" class="font-semibold w-24">Table preset</label>
            <Select id="tablepreset" class="flex-auto" autocomplete="off" v-model="selectedTablePreset"
                :options="settingsStore.tableprests" optionLabel="name" />
        </div>
        <div class="flex items-center gap-4 mb-4">
            <label for="ruleset" class="font-semibold w-24">Ruleset</label>
            <Select id="ruleset" class="flex-auto" autocomplete="off" v-model="selectedRuleset"
                :options="settingsStore.rulesets" optionLabel="name" />
        </div>
        <Divider />
        <div class="flex items-center gap-4 mb-4">
            <label for="player1Name" class="font-semibold w-24">Giocatore 1</label>
            <InputText type="text" v-model="player1Name" class="flex-auto" />
        </div>
        <div class="flex items-center gap-4 mb-4">
            <label for="player2Name" class="font-semibold w-24">Giocatore 2</label>
            <InputText type="text" v-model="player2Name" class="flex-auto" />
        </div>
        <div class="flex justify-end gap-2">
            <Button type="button" label="Annulla" severity="secondary" @click="closeDialog"></Button>
            <Button type="button" label="Crea" @click="newGame"></Button>
        </div>
    </Dialog>
</template>