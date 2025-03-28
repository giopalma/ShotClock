<script setup>
import SetupTimerComponent from '../components/SetupTimerComponent.vue';
import SettingsComponent from '../components/SettingsComponent.vue';
import Footer from '../components/Footer.vue';
</script>

<template>
  <div class="flex flex-col min-h-screen">
    <div class="flex flex-col md:flex-row w-full flex-1">
      <SetupTimerComponent class="md:self-start" />
      <SettingsComponent class="md:self-start" />
    </div>
    <Footer class="mt-auto" />
  </div>
</template>