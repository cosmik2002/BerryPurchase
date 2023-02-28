<template>
  <q-dialog>
    <q-card>
      <q-card-section>{{ message.customer.name }}</q-card-section>
      <q-card-section>{{ message.customer.number }}</q-card-section>
      <q-card-section>
        <q-select
          label="Clients"
          v-model="client"
          :options="clients"
          option-label="name"
          option-value="id"
          :option-disable="(item) => item.customers.length > 0"
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
    oldClient: null
  }),
  computed: {
    clients() {
      return Client.query().orderBy('name').all();
    }
  },
  methods: {
    getClients() {
      Client.api().get('http://localhost:5000/clients', {persistBy: 'create'});
    },

    saveCustomerToClient() {
      CustomersToClients.api().post('http://localhost:5000/customers_to_clients', {
        client_id: this.client.id,
        customer_id: this.message.customer.id
      }).then((results) => {
        if (this.oldClient) {
          CustomersToClients.delete([this.message.customer.id, this.oldClient.id]);
        }
      });
      this.$emit('close');
    }
  },
  beforeUpdate() {
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
