<script setup>
import { Panel, Select, Button, Divider } from 'primevue';
import { useSettingsStore } from '../store';
import { ref, onMounted } from 'vue';
import NewTablePresetModal from './NewTablePresetModal.vue';

const settingsStore = useSettingsStore()
const selectedRuleset = ref(null)
const selectedTablePreset = ref(null)

const reloadSettings = async () => {
    settingsStore.fetchTablePresetsRulesets()
}

const addTablePreset = async () => {
    console.log("Add Table Preset")
    newTableDialogVisible.value = true

}

const addRuleset = async () => {
    console.log("Add Ruleset")
}

onMounted(() => {
    reloadSettings();
});
const newTableDialogVisible = ref(false)
</script>
<template>
    <Panel header="Settings Panel">
        <template #icons>
            <Button icon="pi pi-refresh" severity="secondary" @click="reloadSettings" rounded text />
        </template>
        <div class=" flex flex-col w-md">
            <Select id="tablepreset" ref="tablepresetref" class="flex-auto" autocomplete="off"
                v-model="selectedTablePreset" :options="settingsStore.tableprests" optionLabel="name" showClear
                placeholder="Table Preset">
                <template #footer>
                    <div class="p-3">
                        <Button @click="addTablePreset" label="Aggiungi" fluid severity="secondary" text size="small"
                            icon="pi pi-plus" />
                    </div>
                </template>
            </Select>
            <Divider />
            <Select id="ruleset" class="flex-auto" autocomplete="off" v-model="selectedRuleset"
                :options="settingsStore.rulesets" optionLabel="name" showClear placeholder="Ruleset">
                <template #footer>
                    <div class="p-3">
                        <Button @click="addRuleset" label="Aggiungi" fluid severity="secondary" text size="small"
                            icon="pi pi-plus" />
                    </div>
                </template>
            </Select>
        </div>
        <NewTablePresetModal v-model:visible="newTableDialogVisible" />
    </Panel>
</template>