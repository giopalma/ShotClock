<script setup>
import { socket } from "./socket"
import { Toast } from "primevue";

socket.connect()

</script>
<template>
  <main>
    <Toast :life="3000" />
    <RouterView />
  </main>
</template>