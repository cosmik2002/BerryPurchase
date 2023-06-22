<template>
  <q-item>
    <q-item-section>
      {{item.id}}
      {{item.name}}
  </q-item-section>
  </q-item>
</template>

<script>
export default {
  name: "ClientItem",
    props: {
      item:{}
    },
}
</script>

<style scoped>

</style>
