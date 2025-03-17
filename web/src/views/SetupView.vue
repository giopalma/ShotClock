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
  <div class="flex">
    <SettingsComponent />
    <SetupTimerComponent />
  </div>
</template>