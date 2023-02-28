
const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/IndexPage.vue') },
      { path: 'messages', component: () => import('components/Messages/MessagesList.vue') },
      { path: 'clientslinks', component: () => import('components/ClientsLinks.vue') },
      { path: 'payments', component: () => import('components/Payments/PaymentsList.vue') },
      { path: 'clients', component: () => import('components/ClientsList.vue') },
      { path: 'store', component: () => import('components/StoreTest.vue') }
    ]
  },
/*  {
    path: '/messages',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: 'messages', component: () => import('components/MessagesList.vue') }
    ]
  },*/
  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  }
]

export default routes
