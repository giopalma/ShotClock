<script setup>
import { Panel, ConfirmPopup, Button, Divider, DataTable, Column, useConfirm } from 'primevue';
import { useSettingsStore } from '../store';
import { ref, onMounted } from 'vue';
import NewTablePresetModal from './NewTablePresetModal.vue';
import NewRulesetModal from './NewRulesetModal.vue';

const settingsStore = useSettingsStore()

const reloadSettings = async () => {
    settingsStore.fetchTablePresetsRulesets()
}

const addTablePreset = async () => {
    newTableModalVisible.value = true
}

const deleteTablePreset = async (id) => {
    settingsStore.deleteTablePreset(id)
}

const addRuleset = async () => {
    newRulesetModalVisible.value = true
}

const deleteRuleset = async (id) => {
    settingsStore.deleteRuleset(id)
}

const confirm = useConfirm()

const showConfirm = (event, type, id) => {
    confirm.require({
        target: event.currentTarget,
        message: 'Sei sicuro di voler eliminare l\'elemento?',
        icon: 'pi pi-exclamation-triangle',
        acceptLabel: "Sì",
        acceptProps: {
            severity: "danger"
        },
        rejectLabel: "No",
        rejectProps: {
            severity: "secondary"
        },
        accept: () => {
            if (type === 'table') {
                deleteTablePreset(id)
            } else if (type === 'ruleset') {
                deleteRuleset(id)
            }
        },
    });
}

onMounted(() => {
    reloadSettings();
});
const newTableModalVisible = ref(false)
const newRulesetModalVisible = ref(false)
</script>
<template>
    <Panel header="Settings Panel" class="w-full max-w-md" toggleable>
        <template #icons>
            <Button icon="pi pi-refresh" severity="secondary" @click="reloadSettings" rounded text />
        </template>
        <div class=" flex flex-col">
            <DataTable :value="settingsStore.tableprests" tableStyle="max-width: 50rem" size="small" stripedRows>
                <template #header>
                    <div class="flex flex-wrap items-center justify-between gap-2">
                        <span class="text font-bold">Table Preset</span>
                        <Button @click="addTablePreset" icon="pi pi-plus" rounded text severity="secondary" />
                    </div>
                </template>
                <Column field="name" header="Name"></Column>
                <Column field="id" header="" bodyStyle="text-align: right;">
                    <template #body="slotProps">
                        <ConfirmPopup></ConfirmPopup>
                        <Button @click="showConfirm($event, 'table', slotProps.data.id)" label="Elimina" text
                            severity="danger" />
                    </template>
                </Column>
            </DataTable>
            <Divider />
            <DataTable :value="settingsStore.rulesets" tableStyle="max-width: 50rem" size="small" stripedRows>
                <template #header>
                    <div class="flex flex-wrap items-center justify-between gap-2">
                        <span class="text font-bold">Ruleset</span>
                        <Button @click="addRuleset" icon="pi pi-plus" rounded text severity="secondary" />
                    </div>
                </template>
                <Column field="name" header="Name"></Column>
                <Column field="id" header="" bodyStyle="text-align: right;">
                    <template #body="slotProps">
                        <Button @click="showConfirm($event, 'ruleset', slotProps.data.id)" label="Elimina" text
                            severity="danger" />
                    </template>
                </Column>
            </DataTable>
        </div>
        <NewTablePresetModal v-model:visible="newTableModalVisible" />
        <NewRulesetModal v-model:visible="newRulesetModalVisible" />
    </Panel>
</template>