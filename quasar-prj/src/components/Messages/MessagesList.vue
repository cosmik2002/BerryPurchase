<template>
  <q-checkbox v-model="hide_orders">Hide orders</q-checkbox>
  <q-checkbox v-model="hide_empty">Скрыть без заказа</q-checkbox>
  <q-input label="Поиск" v-model="src_c"></q-input>
  <q-list separator>
    <wa-message v-for="item in messages"
                :key="item.id"
                :item="item"
                @show_customer_to_client_dialog="showCustomerToClientDialog"
                @show_message_order_dialog="showMessageOrderDialog"
                @show_itog_dialog="showItogDialog"
    @delete_message="deleteMessage">

    </wa-message>
  </q-list>
  <div class="pagination">
    <q-btn class="parev_page" v-if="page>1" @click="page--; getMessages()">Prev</q-btn>
    <div class="page_number"> {{ page }}</div>
    <q-btn class="next_page" @click="page++; getMessages()">Next</q-btn>
  </div>

  <customer-to-client-dialog v-model="customer_to_client_dialog" :message="message"
                             @close="closeCustomerToClientDialog(message)"></customer-to-client-dialog>

  <message-order-dialog v-model="message_order_dialog" :message="message" @close="closeMessageOrderDialog(message)"/>
  <itog-dialog v-model="itog_dialog" :itog="itog" @close="itog_dialog=false"></itog-dialog>
</template>
<script>

import axios from 'axios';
import WaMessage from "components/Messages/WaMessage.vue";
import CustomerToClientDialog from "components/Messages/CustomerToClientDialog.vue";
import MessageOrderDialog from "components/Messages/MessageOrderDialog.vue";
import {Message} from "src/store/berries_store/models";
import ItogDialog from "components/Reports/itogDialog.vue";
import itogDialog from "components/Reports/itogDialog.vue";

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
    has_order: false,
    itog: {},
    itog_dialog: false
  }),
  components: {
    WaMessage,
    CustomerToClientDialog,
    MessageOrderDialog,
    ItogDialog
  },
  computed: {
    itogDialog() {
      return itogDialog
    },
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
    src_c: {
      get() {
        return this.search;
      },
      set(val) {
        this.search = val;
        this.getMessages();
      }
    },
    messages() {
      if(this.hide_o || this.hide_e){
      return Message.query().where((msg)=> (this.hide_o ? msg.order_descr=='' : true) && (this.hide_e ? !(msg.props && msg.props.empty) : true))
        .with('for_client').with('customer').with('customer.clients').orderBy('timestamp').all();
      }
      return Message.query().with('for_client').with('customer').with('customer.clients').orderBy('timestamp').all();
    }
  },
  methods: {
    deleteMessage(item) {
      Message.api().delete("messages/" + item.id, {delete: item.id});
    },
    showItogDialog(item){
      if (item.customer.clients.length > 0) {
        const client_id = item.customer.clients[0].id;
        axios.get(path + '/get_orders/' + client_id).then((res) => {
          this.itog = res.data;
          this.itog_dialog = true;
        }).catch((error) => {
          console.error(error);
        });
      }
    },
    showCustomerToClientDialog(item) {
      this.message = item;
      this.customer_to_client_dialog = true;
    },
    closeCustomerToClientDialog(item) {
      Message.api().get('messages/' + item.id);
      this.customer_to_client_dialog = false;
    },
    showMessageOrderDialog(item, index) {
      this.message = item;
      this.message_order_dialog = true;
    },
    closeMessageOrderDialog(item) {
      Message.api().get('messages/' + item.id);
      this.message_order_dialog = false;
    },
    getMessages() {
      this.setSetings();
      let url = 'messages';
      let params = '';
      if (this.search)
        params += `search=${this.search}`;
      if (this.hide_o)
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
    },
    setSetings(){
      localStorage.setItem('mes_prop', JSON.stringify({
        'search': this.search,
        'hide_o': this.hide_o,
        'hide_e': this.hide_e,
        'page': this.page,
        'page_size': this.page_size,
        'date': new Date().toISOString()
      }));
    },
    getSettings(){
      let settings = JSON.parse(localStorage.getItem('mes_prop'));
      if(!settings)
        return;
      if((new Date() - new Date(settings.date))/(1000 * 60 * 60 * 24)<1){
        this.hide_e = settings.hide_e;
        this.hide_o = settings.hide_o;
        this.search = settings.search;
        this.page = settings.page;
        this.page_size = settings.page_size;
      }
    }
  },
  created() {
    this.getSettings();
    this.getMessages();
  }
}
</script>
