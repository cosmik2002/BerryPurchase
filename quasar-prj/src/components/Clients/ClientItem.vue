<template>
  <q-item>
    <q-item-section>
      {{item.id}}
      {{item.name}}
      {{item.duplicate_for}}
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
