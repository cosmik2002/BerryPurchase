<template>
  <q-btn @click="startWaClient()">Запустить Watsapp</q-btn>
  <q-btn @click="loadMessages()">Load Messages</q-btn>
  <q-checkbox v-model="hide_orders">Hide orders</q-checkbox>
  <div>{{ result }}</div>
  <q-list separator>
    <wa-message v-for="item in messages"
                :key="item.id"
                :item="item"
                @show_customer_to_client_dialog="showCustomerToClientDialog"
                @show_message_order_dialog="showMessageOrderDialog">

    </wa-message>
  </q-list>
  <customer-to-client-dialog v-model="customer_to_client_dialog" :message="message"
                             @close="customer_to_client_dialog=false"></customer-to-client-dialog>

  <message-order-dialog v-model="message_order_dialog" :message="message" @close="message_order_dialog=false"/>
</template>
<script>

import axios from 'axios';
import WaMessage from "components/Messages/WaMessage.vue";
import CustomerToClientDialog from "components/Messages/CustomerToClientDialog.vue";
import MessageOrderDialog from "components/Messages/MessageOrderDialog.vue";
import {Message} from "src/store/berries_store/models";

const path = 'http://localhost:5000';

export default {
  name: 'MessagesList',
  data: () => ({
    message: null,
    hide_o: false,
    customer_to_client_dialog: false,
    message_order_dialog: false,
    result: {},
    page: 1,
    page_size: 20,
    search: '',
    has_order: false
  }),
  components: {
    WaMessage,
    CustomerToClientDialog,
    MessageOrderDialog
  },
  computed: {
    hide_orders: {
      get() {
        return this.hide_o;
      },
      set(val) {
        this.hide_o = val;
        this.getMessages()
      }
    },
    messages() {
      return Message.query().with('customer').with('customer.clients').orderBy('timestamp', 'desc').all();
    }
  },
  methods: {
    showCustomerToClientDialog(item) {
      this.message = item;
      this.customer_to_client_dialog = true;
    },
    showMessageOrderDialog(item, index) {
      this.message = item;
      this.message_order_dialog = true;
    },
    startWaClient() {
      axios.get(path + '/start_wa_client').then((res) => {
        this.result = res.data;
      }).catch((error) => {
        console.error(error);
      });
    },
    loadMessages() {
      axios.get(path + '/load_messages').then((res) => {
        this.result = res.data;
      }).catch((error) => {
        console.error(error);
      });
    },
    getMessages() {
      let url = 'http://localhost:5000/messages';
      let params = '';
      if (this.search)
        params += `search=${this.search}`;
      if (this.has_order)
        params += (params !== '' ? '&' : '') + `has_order=1`;
      params += (params !== '' ? '&' : '') + `page=${this.page}`;
      params += (params !== '' ? '&' : '') + `page_size=${this.page_size}`;
      url += '?' + params;
      Message.api().get(url, {persistBy: 'create'});
    }
  },
  created() {
    this.getMessages();
  }
}
</script>
