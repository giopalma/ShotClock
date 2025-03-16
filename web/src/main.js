
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { router } from './router'
import PrimeVue from 'primevue/config'
import Aura from '@primeuix/themes/aura';

import App from './App.vue'
import './styles.css'
const pinia = createPinia()
const app = createApp(App)

app.use(router)
app.use(pinia)
app.use(PrimeVue, {
    theme: {
        preset: Aura
    }
})
app.mount('#app')
