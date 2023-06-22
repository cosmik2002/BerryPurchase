<template>
  <q-dialog scrollable max-width="30%">
    <q-card style="min-width: 300px">
      <q-card-section>
<!--
        <q-card-section>
          <div>Плательщик</div>
          <div>{{ payment.payer.name }}</div>
          <div>{{ payment.payer.card_number }}</div>
        </q-card-section>
-->
        <q-select
          label="Payers"
          v-model="payer"
          :options="payers"
          option-label="name"
          use-input
          @filter="filterFnPayer"
          option-value="id"/>
        <q-select
          label="Clients"
          v-model="client"
          :options="clients"
          option-label="name"
          use-input
          @filter="filterFnCli"
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
import {Client, Payer, Payment} from "src/store/berries_store/models";
import PayersToClients from "../../store/berries_store/models/PayersToClients";
import {Notify} from 'quasar'

export default {
  name: "PayerToClientDialog",
  props: ['payment'],
  emits: ['close'],
  data: () => ({
    client: null,
    payer: null,
    oldClient: null,
    oldPayer: null,
    cliSearch: '',
    payersSearch: ''
  }),
  computed: {
    clients() {
      if (this.cliSearch === '') {
        return Client.query().orderBy('name').all();
      } else {
        let val = this.cliSearch.toLowerCase();
        return Client.query().where((client) => client.name.toLowerCase().indexOf(val) > -1).orderBy('name').all();
      }
    },
    payers() {
      if (this.payersSearch === '') {
        return Payer.query().orderBy('name').all();
      } else {
        let val = this.payersSearch.toLowerCase();
        return Payer.query().where((payer) => payer.name.toLowerCase().indexOf(val) > -1).orderBy('name').all();
      }
    }
  },
  methods: {
    savePayerToClient() {
      if (!this.payer) {
        Notify.create("Необходимо задать плательщика");
        return;
      }
      if (this.oldPayer !== this.payer){
        Payment.api().post('payments', {
          payment_id: this.payment.id,
          payer_id: this.payer.id
        })
        // this.$api.post(`payments/${this.payment.id}`, {
        //   payment_id: this.payment.id,
        //   payer_id: this.payer.id
        // })
      }
      PayersToClients.api().post('payers_to_clients', {
        client_id: this.client ? this.client.id : null,
        payer_id: this.payer.id
      }).then((results) => {
        if (this.oldClient) {
          PayersToClients.delete([this.payer.id, this.oldClient.id]);
        }
      });
      this.$emit('close');
    },
    filterFnCli(val, update) {
      update(() => {
        this.cliSearch = val;
      })
    },
    filterFnPayer(val, update) {
      update(() => {
        this.payersSearch = val;
      })
    },
  },
  beforeUpdate() {
    if (this.payment && this.payment.payer && this.payment.payer.clients.length > 0) {
      this.client = this.payment.payer.clients[0];
      this.oldClient = this.payment.payer.clients[0];
    } else {
      this.client = null;
      this.oldClient = null;
    }
    if (this.payment && this.payment.payer) {
      this.payer = this.payment.payer;
      this.oldPayer = this.payment.payer;
    } else {
      this.payer = null;
      this.oldPayer = null;
    }
  },
  mounted() {
    Client.api().get('clients');
    Payer.api().get('payers');
  }
}
</script>

<style scoped>

</style>
