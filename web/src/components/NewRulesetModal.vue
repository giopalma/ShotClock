<script setup>
import { Dialog, Button, InputText } from 'primevue';
import { ref, watch } from 'vue';
import { useSettingsStore } from '../store';

const settingsStore = useSettingsStore();
const props = defineProps({
    visible: Boolean
});
const emit = defineEmits(['update:visible']);

const closeDialog = () => {
    emit('update:visible', false);
};

const newRuleset = async () => {
    await settingsStore.addRuleset(name.value, initial_duration.value, turn_duration.value, allarm_time.value, increment_duration.value, max_increment_for_match.value
    )
    closeDialog()
}

watch(() => props.visible, (v) => {
    if (v) {
        name.value = ""
    }
});

const name = ref("")
const initial_duration = ref(60)
const turn_duration = ref(35)
const allarm_time = ref(10)
const increment_duration = ref(25)
const max_increment_for_match = ref(1)
</script>
<template>
    <Dialog :visible="visible" @update:visible="emit('update:visible', $event)" modal header="Nuovo Ruleset"
        class="w-md">
        <span class="text-surface-500 dark:text-surface-400 block mb-8">
            Aggiungi delle nuove regole.
        </span>
        <div class="flex items-center gap-4 mb-4">
            <label for="name" class="font-semibold w-12">Nome</label>
            <InputText type="text" v-model="name" class="flex-auto" :invalid="!name" />
        </div>
        <div class="flex items-center gap-4 mb-4">
            <label for="initial_duration" class="font-semibold flex-auto">Durata colpo di apertura</label>
            <InputText type="number" v-model="initial_duration" class="flex-auto" />
        </div>
        <div class="flex items-center gap-4 mb-4">
            <label for="turn_duration" class="font-semibold w-1/2">Durata turno</label>
            <InputText type="number" v-model="turn_duration" class="flex-auto" :invalid="!turn_duration" />
        </div>
        <div class="flex items-center gap-4 mb-4">
            <label for="allarm_time" class="font-semibold w-1/2">Avviso acustico</label>
            <InputText type="number" v-model="allarm_time" class="flex-auto" />
        </div>
        <div class="flex items-center gap-4 mb-4">
            <label for="increment_duration" class="font-semibold w-1/2">Tempo di incremento</label>
            <InputText type="number" v-model="increment_duration" class="flex-auto"
                :invalid="!increment_duration && max_increment_for_match != 0" />
        </div>
        <div class="flex items-center gap-4 mb-4">
            <label for="max_increment_for_match" class="font-semibold w-1/2">Massimi incrementi per gioco</label>
            <InputText type="number" v-model="max_increment_for_match" class="flex-auto"
                :invalid="!max_increment_for_match" />
        </div>
        <div class="flex justify-end gap-2">
            <Button type="button" label="Annulla" severity="secondary" @click="closeDialog"></Button>
            <Button type="button" label="Crea" @click="newRuleset" :disabled="!name"></Button>
        </div>
    </Dialog>
</template>