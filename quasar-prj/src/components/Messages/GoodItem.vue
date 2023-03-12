<template>
<q-item clickable>
  <q-item-section>
    {{good.name}}
  </q-item-section>
  <q-item-section>
    {{good.variants}}
  </q-item-section>
</q-item>
</template>

<script>
export default {
  name: "GoodItem",
  props: ['good']
}
</script>

<style scoped>
</style>
