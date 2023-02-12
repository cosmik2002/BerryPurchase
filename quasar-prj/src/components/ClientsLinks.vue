`<template>
  <q-list>
    <q-item v-for="item in clientsLinks"
            :key="item.client_id" clickable @click="showDlgClick(item)">
      <q-item-section>
        <q-item-label>{{ item.client.name }}</q-item-label>
        <q-item-label>{{ item.customer.number }}</q-item-label>
        <q-item-label>{{ item.payer.name }}</q-item-label>
      </q-item-section>
    </q-item>
  </q-list>
  <q-dialog v-model="dialog" scrollable max-width="30%">
    <q-card>
      <q-card-section>
        Title
        <q-select
          label="Clients"
          v-model="clientLink.client"
          :options="clients"
          option-label="name"
          option-value="id"/>
        <q-select
          label="Customers"
          v-model="clientLink.customer"
          :options="customers"
          :option-label="customerTitle"
          option-value="id" />
        <q-select
          label="Payers"
          v-model="clientLink.payer"
          :options="payers"
          option-label="name"
          option-value="id" />
      </q-card-section>
      <q-card-actions>
        <q-btn @click="saveClientLink">save</q-btn>
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script>
import axios from "axios";

const path = 'http://localhost:5000';
export default {
  name: "ClientsLinks",
  data: () => ({
    clientsLinks: [],
    clients: [],
    customers: [],
    payers: [],
    clientLink: [],
    dialog: false
  }),
  methods: {
    customerTitle(item) {
      return item.number + item.push_name;
    },
    saveClientLink(link) {
      axios.post(path + '/clients_links', this.clientLink);
    },
    getClientsLinks() {
      axios.get(path + '/clients_links').then((res) => {
        this.clientsLinks = res.data;
      }).catch((error) => {
        console.error(error);
      });
    },
    async showDlgClick(item) {
      if (!this.loaded) {
        this.loaded = true;
        await axios.get(path + '/clients').then((res) => {
          this.clients = res.data;
        }).catch((error) => {
          console.error(error);
        });
        await axios.get(path + '/customers').then((res) => {
          this.customers = res.data;
        }).catch((error) => {
          console.error(error);
        });
        await axios.get(path + '/payers').then((res) => {
          this.payers = res.data;
        }).catch((error) => {
          console.error(error);
        });
        this.clientLink = item;
        this.dialog = true;
      } else {
        this.clientLink = item;
        this.dialog = true;
      }
    },
  },
  created() {
    this.getClientsLinks();
  }
}
</script>

<style scoped>

</style>
`
