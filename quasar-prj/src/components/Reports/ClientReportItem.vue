<template>
      {{client}}
  <q-card>

      <div v-for="(gval, gkey) in goods"
              :key="gkey">
        {{gkey}}-{{gval}}
      </div>
  </q-card>
</template>

<script>
export default {
  name: "ClientReportItem",
  props:{
    client:null,
    goods: null
  }
}
</script>

<style scoped>

</style>
