<template>
  <q-checkbox v-model="hide_orders">Hide orders</q-checkbox>
  <q-checkbox v-model="hide_empty">Hide empty</q-checkbox>
  <div>{{ result }}</div>
  <q-list separator>
    <wa-message v-for="item in messages"
                :key="item.id"
                :item="item"
                @show_customer_to_client_dialog="showCustomerToClientDialog"
                @show_message_order_dialog="showMessageOrderDialog">

    </wa-message>
  </q-list>
    <div class="pagination">
    <q-btn class="parev_page" v-if="page>1" @click="page--; getMessages()">Prev</q-btn>
    <div class="page_number"> {{ page }}</div>
    <q-btn class="next_page" @click="page++; getMessages()">Next</q-btn>
  </div>

  <customer-to-client-dialog v-model="customer_to_client_dialog" :message="message"
                             @close="customer_to_client_dialog=false"></customer-to-client-dialog>

  <message-order-dialog v-model="message_order_dialog" :message="message" try-to @close="closeMessageOrderDialog(message)"/>
</template>
<script>

import axios from 'axios';
import WaMessage from "components/Messages/WaMessage.vue";
import CustomerToClientDialog from "components/Messages/CustomerToClientDialog.vue";
import MessageOrderDialog from "components/Messages/MessageOrderDialog.vue";
import {Message} from "src/store/berries_store/models";

const path = process.env.API_URL;

export default {
  name: 'MessagesList',
  data: () => ({
    message: null,
    hide_o: false,
    hide_e: false,
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
    hide_empty: {
      get() {
        return this.hide_e;
      },
      set(val) {
        this.hide_e = val;
        this.getMessages()
      }
    },
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
      return Message.query().with('customer').with('customer.clients').all();
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
    closeMessageOrderDialog(item) {
      Message.api().get('messages/'+item.id);
      this.message_order_dialog = false;
    },
    getMessages() {
      let url = 'messages';
      let params = '';
      if (this.search)
        params += `search=${this.search}`;
      if (this.has_order)
        params += (params !== '' ? '&' : '') + `has_order=1`;
      if (this.hide_e)
        params += (params !== '' ? '&' : '') + `hide_empty=1`;
      params += (params !== '' ? '&' : '') + `page=${this.page}`;
      params += (params !== '' ? '&' : '') + `page_size=${this.page_size}`;
      url += '?' + params;
      Message.api().get(url, {
        persistBy: 'create',
        persistOptions: {
          insertOrUpdate: ['customer', 'clients']
        }
      });
    }
  },
  created() {
    this.getMessages();
  }
}
</script>
