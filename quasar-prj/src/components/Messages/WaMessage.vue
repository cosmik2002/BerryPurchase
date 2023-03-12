<template>
  <q-item
    :class="itemClass(item)">
    <q-item-section>
      <q-item-label>{{item.id}} {{ item.timestamp }}</q-item-label>
      <q-item-label>{{ item.customer.name }} {{ item.customer.number }}</q-item-label>
      <q-item-label>{{ item.customer.push_name }}</q-item-label>
      <q-item-label> {{ item.text }}</q-item-label>
      <q-item-label>
        <q-btn round :color="item.order_descr == '' ? 'red' : 'green'" icon="local_grocery_store" @click="$emit('show_message_order_dialog', item)"></q-btn>
        {{ item.order_descr }}
      </q-item-label>
    </q-item-section>
    <q-item-section side top>
      <div v-if="item.customer.clients.length>0">Клиент: {{ item.customer.clients[0].name }}</div>
      <q-btn round icon="face" @click="$emit('show_customer_to_client_dialog', item)"></q-btn>
    </q-item-section>
  </q-item>
</template>
<script>
export default {
  name: "WaMessage",
  props: ['item'],
  emits: ['show_customer_to_client_dialog', 'show_message_order_dialog'],
  data: () => ({
    customer_to_client_dialog: false,
  }),
  methods: {
    itemClass() {
      if (this.item.customer && this.item.customer.clients.length > 0) {
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
