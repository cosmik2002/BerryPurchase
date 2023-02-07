<template>
  <v-container> <!-- Создаем контейнер внутри которого и будут элементы компонента -->
    <v-btn @click="showDlgClick"></v-btn>
  <v-list>
    <v-list-item v-for="item in clientsLinks"
    :key="item.client_id"
    :title="item.client.name"
    :subtitle="item.customer.number"
     @click.stop="showDlgClick(item.wa_id)">
    </v-list-item>
  </v-list>
  </v-container>
    <v-dialog v-model="dialog" scrollable max-width="30%">
      <v-card>
        <v-card-title>Title</v-card-title>
        <v-divider></v-divider>
  <v-card-text>
        <v-combobox
          label="Clients"
          v-model="clientLink.client_id"
        :items="clients"
        item-title="name"
        item-value="id">
        </v-combobox>
        <v-combobox
          label="Customers"
          v-model="clientLink.customer_id"
        :items="customers"
        :item-title="customerTitle"
        item-value="id">
        </v-combobox>
        <v-combobox
          label="Payers"
          v-model="clientLink.payer_id"
        :items="payers"
        item-title="name"
        item-value="id">
        </v-combobox>
    </v-card-text>
      <v-btn @click="saveClientLink">save</v-btn>
      </v-card>
    </v-dialog>
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
    customerTitle(item){
      return item.number + item.push_name;
    },
    saveClientLink(link) {
      axios.post(path+'/clients_links',this.clientLink);
    },
    getClientsLinks() {
      axios.get(path+'/clients_links').then((res)=>{
        this.clientsLinks = res.data;
      }).catch((error) => {
        console.error(error);
      });
    },
    showDlgClick(){
      if (!this.loaded) {
        this.loaded = true;
        axios.get(path+'/clients').then((res) => {
          this.clients = res.data;
        }).catch((error) => {
          console.error(error);
        });
        axios.get(path+'/customers').then((res) => {
          this.customers = res.data;
        }).catch((error) => {
          console.error(error);
        });
        axios.get(path+'/payers').then((res) => {
          this.payers = res.data;
        }).catch((error) => {
          console.error(error);
        });
        this.dialog = true;
      } else {
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
