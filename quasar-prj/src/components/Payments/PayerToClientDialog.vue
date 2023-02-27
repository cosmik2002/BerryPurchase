<template>
  <q-dialog scrollable max-width="30%">
    <q-card style="min-width: 300px">
      <q-card-section>
        <q-card-section>
          <div>Плательщик</div>
          <div>{{ payment.payer.name }}</div>
          <div>{{ payment.payer.card_number }}</div>
        </q-card-section>
        <q-select
          label="Clients"
          v-model="client"
          :options="clients"
          option-label="name"
          option-value="id"/>
      </q-card-section>
      <q-card-actions>
        <q-btn @click="$emit('close')">Отмена</q-btn>
        <q-btn @click="savePayerToClient()">Сохранить</q-btn>
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script>
import Client from "src/store/berries_store/models/Clients";
import PayersToClients from "../../store/berries_store/models/PayersToClients";

export default {
  name: "PayerToClientDialog",
  props: ['payment'],
  emits: ['close'],
  data: () =>({
    client: null,
    oldClient: null
  }),
  computed: {
    clients() {
      return Client.query().orderBy('name').all();
    }
  },
  methods: {
    savePayerToClient () {
      PayersToClients.api().post('http://localhost:5000/payers_to_clients', {
        client_id: this.client.id,
        payer_id: this.payment.payer.id
      }).then((results) => {
        if (this.oldClient) {
          PayersToClients.delete([this.payment.payer.id, this.oldClient.id]);
        }
      });
      this.$emit('close');
    }
  },
  beforeUpdate() {
      if (this.payment && this.payment.payer.clients.length > 0) {
        this.client = this.payment.payer.clients[0];
        this.oldClient = this.payment.payer.clients[0];
      } else {
        this.client = null;
        this.oldClient = null;
      }
  },
  mounted() {
    Client.api().get('http://localhost:5000/clients');
  }
}
</script>

<style scoped>

</style>
