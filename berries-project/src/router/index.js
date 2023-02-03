// Composables
import { createRouter, createWebHistory } from 'vue-router'
import MessagesList from '../components/MessagesList.vue'

const routes = [
  {
    path: '/',
    name: 'MessageList',
    component: MessagesList
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
})

export default router
