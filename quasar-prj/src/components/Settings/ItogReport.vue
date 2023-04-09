<template>
<q-list dense>
  <q-item v-for="(row, index) in res1" :key="index">
    {{index}} {{row}}
  </q-item>
</q-list>
  <div v-for="(row, index) in res2" :key="index">
    {{index}}-{{row}}
  </div>
</template>

<script>
export default {
  name: "ItogReport",
  props:['report_data'],
  computed:{
    res1() {
      if (this.report_data) {
        return Object.fromEntries(Object.entries(this.report_data['res']).filter(([key,value])=>value));
      }
      return [];
    },
    res2() {
      if (this.report_data) {
        return Object.fromEntries(Object.entries(this.report_data['0']).filter(([key,value])=>value));
      }
      return [];
    }
  }
}
</script>

<style scoped>

</style>
