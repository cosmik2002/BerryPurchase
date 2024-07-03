<template>
  <q-dialog>
    <q-card>
      <q-card-section>{{ message.customer.name }}</q-card-section>
      <q-card-section>{{ message.customer.number }}</q-card-section>
      <q-card-section>
        <q-select
          label="Clients"
          v-model="client"
          :options="options"
          use-input
          option-value="id"
          @filter="filterFn"
          :option-label="(item) => (item && item.customers && item.customers.length > 0) ? 'x '+item.name : item.name"
        >
          <template v-slot:append>
            <q-btn round dense flat icon="add" @click.stop.prevent="addClient"/>
          </template>

        </q-select>
        <q-select
          label="Заказ для другого"
          v-model="forClient"
          :options="options"
          use-input
          option-label="name"
          option-value="id"
          @filter="filterFn"
        />
      </q-card-section>
      <q-card-section>
        {{ this.message.text }}
      </q-card-section>
      <q-card-actions>
        <q-btn @click="$emit('close')">Отмена</q-btn>
        <q-btn @click="saveCustomerToClient()">Сохранить</q-btn>
      </q-card-actions>
    </q-card>
    <q-dialog v-model="client_add_dialog">
      <q-card>
        <q-card-section>
          <q-input v-model="client_name"></q-input>
        </q-card-section>
        <q-card-actions>
          <q-btn @click="client_add_dialog=false">Отмена</q-btn>
          <q-btn @click="addClient($event, client_name)">Сохранить</q-btn>
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-dialog>
</template>

<script>
import {Client, CustomersToClients, Message} from "src/store/berries_store/models";

export default {
  name: "CustomerToClientDialog",
  props: ["message"],
  emits: ['close'],
  data: () => ({
    client: null,
    forClient: null,
    oldClient: null,
    options: null,
    client_add_dialog: false,
    client_name: ''
  }),
  computed: {
    clients() {
      return Client.query().orderBy('name').all();
    }
  },
  methods: {
    async addClient(ev, data) {
      console.log(ev);
      console.log(data);
      if (data) {
        let result = await Client.api().post('clients', {
          name: data
        })
        this.client = result.entities.clients[0];
        this.client_add_dialog = false;
      } else {
        this.client_name = this.message.customer.name;
        this.client_add_dialog = true;
      }
    },
    getClients() {
      Client.api().get('clients');
    },
    filterFn(val, update) {
      if (val === '') {
        update(() => {
          this.options = this.clients;
        })
        return
      }

      update(() => {
        const needle = val.toLowerCase()
        this.options = this.clients.filter(v => v.name.toLowerCase().indexOf(needle) > -1)
      })
    },
    saveCustomerToClient() {
      CustomersToClients.api().post('customers_to_clients', {
        client_id: this.client ? this.client.id : null,
        customer_id: this.message.customer.id,
        message_id: this.message.id,
        for_client_id: this.forClient ? this.forClient.id : null
      }).then((results) => {
        if (this.oldClient && this.oldClient.id !== this.client.id) {
          CustomersToClients.delete([this.message.customer.id, this.oldClient.id]);
        }
      });
      this.$emit('close');
      }
    },
    beforeUpdate() {
      if (this.message && this.message.for_client) {
        this.forClient = this.message.for_client;
      } else {
        this.forClient = null;
      }
      if (this.message && this.message.customer.clients.length > 0) {
        this.client = this.message.customer.clients[0];
        this.oldClient = this.message.customer.clients[0];
      } else {
        this.client = null;
        this.oldClient = null;
      }
    },
    mounted() {
      this.getClients();
    }
  }
</script>

<style scoped>

</style>
