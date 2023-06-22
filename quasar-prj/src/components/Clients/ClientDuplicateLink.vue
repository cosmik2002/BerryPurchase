<template>
<q-dialog>
  <q-card>
    <q-card-section>
              <q-select
          label="Основной"
          v-model="client_from"
          :options="clients"
          option-label="name"
          use-input
          @filter="filterFnCli"
          option-value="id"/>
                    <q-select
          label="Дубль"
          v-model="client_to"
          :options="clients"
          option-label="name"
          use-input
          @filter="filterFnCli"
          option-value="id"/>
    </q-card-section>
  </q-card>
</q-dialog>
</template>

<script>
import {Client} from "src/store/berries_store/models";
import {Notify} from "quasar";

export default {
  name: "ClientDuplicateLink",
  props: ['client'],
  emits: ['close'],
  data: () => ({
    client_from: null,
        client_to: null,
    cliSearch: ''
  }),
  computed: {
    clients() {
      if (this.cliSearch === '') {
        return Client.query().orderBy('name').all();
      } else {
        let val = this.cliSearch.toLowerCase();
        return Client.query().where((client) => client.name.toLowerCase().indexOf(val) > -1).orderBy('name').all();
      }
    }
  },
  methods: {
    filterFnCli(val, update) {
      update(() => {
        this.cliSearch = val;
      })
    },
  },
  beforeUpdate() {
  },
  mounted() {
    Client.api().get('clients');
  }
}

</script>

<style scoped>

</style>
