import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated } from './auth'

const routes = [
    { path: '/', component: () => import('./views/TimerView.vue') },
    {
        path: '/setup',
        component: () => import('./views/SetupView.vue'),
        beforeEnter: async (to, from) => {
            const isAuth = await isAuthenticated()

            if (!isAuth) {
                return { name: 'login', query: { redirect: to.fullPath } }
            }
        }
    },
    { name: 'login', path: '/login', component: () => import('./views/LoginView.vue') }
]

export const router = createRouter({
    history: createWebHistory(),
    routes,
})