// Composables
import { createRouter, createWebHistory } from 'vue-router'
import CafeList from '../components/CafeList.vue'
import CafeView from '../components/CafeView.vue'

const routes = [
  {
    path: '/',
    name: 'CafeList',
    component: CafeList
  },
  {
    path: '/cafe/view',
    name: 'CafeView',
    component: CafeView
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
})

export default router
