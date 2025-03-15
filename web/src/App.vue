<script>
import { socket } from "./socket"
export default {
  setup() {
    socket.connect()
  }
}
</script>
<template>
  <main>
    <RouterView />
  </main>
</template>