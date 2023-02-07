// Composables
import { createRouter, createWebHistory } from 'vue-router'
import MessagesList from '../components/MessagesList.vue'
import exampleMy from '../components/example'
import ClientsLinks from "@/components/ClientsLinks";

const routes = [
  {
    path: '/',
    name: 'MessageList',
    component: MessagesList
  },  {
    path: '/clientslinks',
    name: 'ClientsLinks',
    component: ClientsLinks
  }, {
    path: '/ex',
    name: 'example',
    component: exampleMy

  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
})

export default router
