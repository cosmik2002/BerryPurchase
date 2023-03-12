<template>
    <q-item >
      <q-item-section >
        <q-item-label v-if="item.payer">
          <div>Плательщик: {{ item.payer.name }}</div>
          <div>Карта: {{ item.payer.card_number }}</div>
        </q-item-label>
        <q-item-label> {{ new Date(item.timestamp).toLocaleDateString() }}
        </q-item-label>
        <q-item-label>
          Сумма: {{ item.sum }} <span v-if="isOst">Остаток: {{item.ost}}</span>
        </q-item-label>
        <q-item-label>
          {{ item.comment }}
        </q-item-label>
      </q-item-section>
      <q-item-section side top>
        <q-item-label v-if="item.payer && item.payer.clients.length > 0">
          <div>Клиент: {{ item.payer.clients[0].name }}</div>
        </q-item-label>
      </q-item-section>
    <q-separator/>
    </q-item>
</template>

<script>
export default {
  name: "PaymentItem",
  props: ['item', 'isOst'],
  methods: {
        itemClass(item){
      if (item.payer && item.payer.clients.length > 0) {
        return "bg-green-1";
      } else {
        return 'bg-red-1';
      }
    },
  }
}
</script>

<style scoped>

</style>
