<template>
<div>store</div>
  <div>{{clients}}</div>
</template>

<script>
// import { useStore } from 'vuex'
import { mapActions, mapGetters } from 'vuex'
import { createStore } from 'vuex'

export default {
  name: "StoreTest",
/*  data:() => ({
    store: () => {useStore()}
  }),*/
  computed:{
    ...mapGetters('berries_store', ['clients'])
  },
  methods:{
    ...mapActions('berries_store', ['get_clients'])
  },
  mounted() {
    this.get_clients();
  }

}
</script>

<style scoped>

</style>
