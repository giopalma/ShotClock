import { createMemoryHistory, createRouter } from 'vue-router'

import SetupView from './views/SetupView.vue'
import TimerView from './views/TimerView.vue'
import { createWebHistory } from 'vue-router'

const routes = [
    { path: '/', component: TimerView },
    { path: '/setup', component: SetupView },
]

export const router = createRouter({
    history: createWebHistory(),
    routes,
})