<template>
  <q-btn @click="parseClients()">Get Clients From G</q-btn>
  <div> {{ result }}</div>
  <q-list>
    <client-item
      v-for="item in clients"
      :key="item.id"
      :item="item"
    clickable
    @click = 'ClientDup'>
    </client-item>
  </q-list>
<client-duplicate-link v-model="dialog"> </client-duplicate-link>
</template>
<script>

import axios from 'axios';

const path = process.env.API_URL;
import ClientItem from "components/Clients/ClientItem.vue";
import ClientDuplicateLink from "components/Clients/ClientDuplicateLink.vue";
export default {
  name: 'ClientsList',
  data: () => ({
    clients: [],
    dialog: false,
    title: 'null',
    loaded: false,
    result: {}
  }),
  components: {
    ClientItem,
    ClientDuplicateLink
  },
  methods: {
    ClientDup(){
      this.dialog=true
    },
    parseClients() {
      axios.get(path + '/get_clients').then((res) => {
        this.result = res.data;
      }).catch((error) => {
        console.error(error);
      });
    },
    getClients() {
      axios.get(path + '/clients').then((res) => {
        this.clients = res.data;
      }).catch((error) => {
        console.error(error);
      });
    }
  },
  created() {
    this.getClients();
  }
}
</script>
