<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title>
          Ягодный сбор
        </q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
    >
      <q-list>
        <q-item-label
          header
        >
          Разделы
        </q-item-label>

        <EssentialLink
          v-for="link in essentialLinks"
          :key="link.title"
          v-bind="link"
        />
      </q-list>
    </q-drawer>

    <q-page-container style="max-width:2500px">
      <router-view/>
    </q-page-container>
  </q-layout>
</template>

<script>
import { defineComponent, ref } from 'vue'
import EssentialLink from 'components/EssentialLink.vue'

const linksList = [
  {
    title: 'Сообщения',
    // caption: 'Messages',
    icon: 'list',
    link: '/messages'
  },
  {
    title: 'Платежи',
    icon: 'credit_card',
    link: '/payments'
  },
  {
    title: 'Клиенты',
    icon: 'record_voice_over',
    link: '/clients'
  },
  {
    title: 'Служебные',
    icon: 'settings',
    link: '/settings'
  },
  {
    title: 'Товары',
    icon: 'shopping_basket',
    link: '/goods'
  },
  {
    title: 'Отчеты',
    icon: 'assignment',
    link: '/reports'
  }
]

export default defineComponent({
  name: 'MainLayout',

  components: {
    EssentialLink
  },

  setup () {
    const leftDrawerOpen = ref(false)

    return {
      essentialLinks: linksList,
      leftDrawerOpen,
      toggleLeftDrawer () {
        leftDrawerOpen.value = !leftDrawerOpen.value
      }
    }
  }
})
</script>
