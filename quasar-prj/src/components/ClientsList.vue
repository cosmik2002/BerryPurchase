<template>
  <q-btn @click="parseClients()">Get Clients From G</q-btn>
  <div> {{ result }}</div>
  <q-table
  :columns="columns"
  :rows="clients"
  row-key="id">
  </q-table>

</template>
<script>

import axios from 'axios';
const path = process.env.API_URL;

export default {
  name: 'ClientsList',
  data: () => ({
    columns: [
      {
        name: "id",
        label: "id",
        field: "id"
      },      {
        name: "name",
        label: "name",
        field: "name"
      }],
    clients: [],
    dialog: false,
    title: 'null',
    loaded: false,
    result: {}
  }),
  methods:  {
    parseClients() {
      axios.get(path+'/get_clients').then((res)=>{
        this.result = res.data;
      }).catch((error) => {
        console.error(error);
      });
    },
    getClients() {
      axios.get(path+'/clients').then((res)=>{
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
