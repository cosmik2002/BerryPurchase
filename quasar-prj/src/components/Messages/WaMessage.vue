<template>
  <q-card>
    <q-item
      :class="itemClass(item)">
      <q-item-section>
        <img v-if="item.props && (item.props.msg || '' ==='tg')" src="icons/telegram.svg" height="32" width="32"/>
        <q-item-label>{{ formatDate(item.timestamp) }} {{ getCustomerName(item) }} {{
            item.customer ? item.customer.number : ''
          }}
          <span v-if="item.customer && item.customer.clients && item.customer.clients.length>0">Клиент: {{ item.customer.clients[0].name }}</span>
          <span v-if="item.for_client_id">Клиент: {{ item.for_client.name }}</span>
        </q-item-label>
        <q-item-label> {{ item.text }}</q-item-label>
        <q-item-label v-if="item.props && item.props.media && item.props.media.mimetype=='image/jpeg'">
          <img :src="getMedia()" alt="img" height="200">

        </q-item-label>
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
          ({{ item.id }} {{ (item.props || {}).type }})
          <q-chip v-if="(item.props || {}).comment"
                  color="orange" text-color="white">{{ item.props.comment }}
          </q-chip>
        </q-item-label>
      </q-item-section>
      <q-item-section side top>
        <q-btn round dense icon="face" @click="$emit('show_customer_to_client_dialog', item)"></q-btn>
        <q-btn round dense icon="event" @click="$emit('show_itog_dialog', item)"></q-btn>
        <q-btn round dense icon="delete" color="red" @click="delete_dialog=true"></q-btn>
      </q-item-section>
    </q-item>
    <q-dialog v-model="delete_dialog">
      <q-card>
        <q-card-section>
          Удалить сообщение?
        </q-card-section>
        <q-card-actions>
          <q-btn label="OK" @click="$emit('delete_message', item)" v-close-popup/>
          <q-btn label="НЕТ" v-close-popup/>
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-card>
</template>
<script>
const path = process.env.API_URL;
import {Message} from "src/store/berries_store/models";

export default {
  name: "WaMessage",
  props: ['item'],
  emits: ['show_customer_to_client_dialog', 'show_message_order_dialog', 'show_itog_dialog', 'delete_message'],
  data: () => ({
    customer_to_client_dialog: false,
    delete_dialog: false,
    quoted: null
  }),
  methods: {
    getMedia() {
      return path + "/" + this.item.props.media.file;
    },
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
      return new Date(dateStr).toLocaleString();
    },
    getCustomerName(item) {
      if (item.customer) {
        if (item.customer.name)
          return item.customer.name;
        if (item.customer.short_name || item.customer.push_name) {
          return item.customer.short_name ?? '' + " " + item.customer.push_name ?? '';
        }
        return '';
      }
    },
    itemClass() {
      if (this.item.customer && (this.item.customer.clients.length > 0 || this.item.for_client_id)) {
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
