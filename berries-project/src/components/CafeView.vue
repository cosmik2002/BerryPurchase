<!-- src/components/CafeView.vue -->
<template>
  <v-container>

    <CafeInfo></CafeInfo> <!-- Этот компонент мы сейчас создадим -->

  </v-container>
</template>

<script>
import CafeInfo from './CafeInfo.vue'
export default {
  name: 'CafeView',
  components: {
    CafeInfo
  }
}
</script>
