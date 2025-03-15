import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    { path: '/', component: () => import('./views/TimerView.vue') },
    {
        path: '/setup',
        component: () => import('./views/SetupView.vue')
    },
]

export const router = createRouter({
    history: createWebHistory(),
    routes,
})