<template>
  <q-item
    :class="itemClass(item)">
    <q-item-section>
      <q-item-label>{{ formatDate(item.timestamp) }} {{ getCustomerName(item) }} {{
          item.customer ? item.customer.number : ''}}
      <span v-if="item.customer.clients.length>0">Клиент: {{ item.customer.clients[0].name }}</span>
      </q-item-label>
      <q-item-label> {{ item.text }}</q-item-label>
      <q-item-label v-if="item.quoted_id">
        <q-card>{{ quoted ? quoted.text : '' }}</q-card>
      </q-item-label>
      <q-item-label>
        <q-btn round :color="item.order_descr === '' ? 'red' : 'green'" icon="local_grocery_store"
               @click="$emit('show_message_order_dialog', item)"></q-btn>
        {{ item.order_descr }}
        <q-checkbox :model-value="item.props && item.props.empty || false"
                    v-if="item.order_descr==''"
                    @update:model-value="updRow(item, {empty: $event})"
                    label="Нет заказа">
        </q-checkbox>
      </q-item-label>
      <q-item-label>
      </q-item-label>
    </q-item-section>
    <q-item-section side top>
      <q-btn round icon="face" @click="$emit('show_customer_to_client_dialog', item)"></q-btn>
    </q-item-section>
  </q-item>
</template>
<script>
import {Message} from "src/store/berries_store/models";

export default {
  name: "WaMessage",
  props: ['item'],
  emits: ['show_customer_to_client_dialog', 'show_message_order_dialog'],
  data: () => ({
    customer_to_client_dialog: false,
    quoted: null
  }),
  methods: {
    updRow(row, data) {
      let msg = {...this.item};
      msg.props = msg.props ? {...msg.props, ...data} : {...data};
      Message.api().post('messages/' + this.item.id, msg);
    },
    getQuoted(id) {
      this.quoted = Message.find(id);
      if (!this.quoted) {
        Message.api().get("messages/" + id).then((res) => {
          this.quoted = Message.find(id);
        });
      }
      //return "Цитата";
    },
    formatDate(dateStr) {
      return new Date(dateStr).toISOString().slice(0,10);
    },
    getCustomerName(item) {
      if(item.customer) {
        if (item.customer.name)
          return item.customer.name;
        if(item.customer.short_name || item.customer.push_name) {
          return item.customer.short_name ?? '' + " " + item.customer.push_name ?? '';
        }
        return '';
      }
    },
    itemClass() {
      if (this.item.customer && this.item.customer.clients.length > 0) {
        return "bg-green-1";
      } else {
        return 'bg-red-1';
      }
    },
  },
  mounted() {
    if (this.item.quoted_id) {
      this.getQuoted(this.item.quoted_id)
    }
  },
}
</script>

<style scoped>

</style>
