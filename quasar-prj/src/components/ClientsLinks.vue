`<template>
  <q-table
    :columns="columns"
  :rows="clientsLinks"
    :row-key="row=>row.client.id+':'+row.customer.id"
  >
          <template v-slot:top>
      <q-btn icon="add" @click="showDlgClick"></q-btn>
      </template>
    <template v-slot:body-cell-actions="props">
    <q-td :props="props">
      <q-btn icon="mode_edit" @click="onEdit(props.row)"></q-btn>
      <q-btn icon="delete" @click="onDelete(props.row)"></q-btn>
    </q-td>
  </template>
  </q-table>
  <q-dialog v-model="dialog" scrollable max-width="30%">
    <q-card style="min-width: 300px">
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

const path = process.env.API_URL;
export default {
  name: "ClientsLinks",
  data: () => ({
    columns:[{
      name: 'client_id',
      label: 'client_id',
      field: 'client_id'
    },{
      name: 'client_name',
      label: 'client_name',
      field: row => row.client.name
    },{
      name: 'customer_id',
      label: 'customer_id',
      field: row => row.customer.id
    },{
      name: 'customer_name',
      label: 'customer_name',
      field: row => row.customer.name
    },{
      name: 'payer_id',
      label: 'payer_id',
      field: row => row.payer.id
    },{
      name: 'payer_name',
      label: 'payer_name',
      field: row => row.payer.name
    },{
      name: 'actions',
      label: 'Actions'
    }],
    clientsLinks: [],
    clients: [],
    customers: [],
    payers: [],
    clientLink: [],
    oldClientLink: null,
    dialog: false
  }),
  methods: {
    onAdd() {
      console.log("Add");
    },
    onEdit(row) {
      this.clientLink = row
      this.oldClientLink = {...row};
      this.showDlgClick()
      // console.log("edit" + row.client.name);
    },
    onDelete(row) {
      console.log("delete" + row.client.name);
    },
    customerTitle(item) {
      return item.number + item.push_name;
    },
    saveClientLink(link) {
      var config = { headers: {
                      'Content-Type': 'application/json',
                      'Access-Control-Allow-Origin': '*'}
             }
      let data = {...this.clientLink};
      data.client_id = data.client.id;
      data.customer_id = data.customer.id;
      data.payer_id = data.payer.id;
      if (this.oldClientLink) {
        data.oldClientLink = this.oldClientLink;
      }
      axios.post(path + '/clients_links', data);
      this.oldClientLink = null;
      this.dialog = false;
    },
    getClientsLinks() {
      axios.get(path + '/clients_links').then((res) => {
        this.clientsLinks = res.data;
      }).catch((error) => {
        console.error(error);
      });
    },
    async showDlgClick() {
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
`
