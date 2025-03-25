<script>
import { defineComponent } from 'vue';
import SetupTimerComponent from '../components/SetupTimerComponent.vue';
import SettingsComponent from '../components/SettingsComponent.vue';

export default defineComponent({
  components: {
    SetupTimerComponent,
    SettingsComponent
  }
});
</script>

<template>
  <div class="flex flex-col md:flex-row w-full h-full">
    <SetupTimerComponent class="md:self-start" />
    <SettingsComponent class="md:self-start" />
  </div>
</template>