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
          option-label="name"
          option-value="id"
          @filter="filterFn"
           :option-disable="(item) => item && item.customers && item.customers.length > 0"
        />
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
  </q-dialog>
</template>

<script>
import {Client, CustomersToClients} from "src/store/berries_store/models";

export default {
  name: "CustomerToClientDialog",
  props: ["message"],
  emits: ['close'],
  data: () => ({
    client: null,
    forClient: null,
    oldClient: null,
    options: null
  }),
  computed: {
    clients() {
      return Client.query().with('customers').orderBy('name').all();
    }
  },
  methods: {
    getClients() {
      Client.api().get('clients');
    },
      filterFn (val, update) {
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
        if (this.oldClient) {
          CustomersToClients.delete([this.message.customer.id, this.oldClient.id]);
        }
      });
      this.$emit('close');
    }
  },
  beforeUpdate() {
    if(this.message && this.message.for_client){
      this.forClient = this.message.for_client;
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
