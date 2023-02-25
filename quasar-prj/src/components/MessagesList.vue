<template>
  <q-btn @click="startWaClient()">Запустить Watsapp</q-btn>
  <q-btn @click="loadMessages()">Load Messages</q-btn>
  <q-checkbox v-model="hide_orders">Hide orders</q-checkbox>
  <div>{{ result }}</div>
  <q-list separator>
    <q-item v-for="(item, index) in messages"
            :key="item.id" v-ripple:red :class="itemClass(item)">
      <q-item-section>
        <q-item-label>{{ item.timestamp }}</q-item-label>
        <q-item-label>{{ item.customer.name }} {{ item.customer.number }}</q-item-label>
        <q-item-label>{{ item.customer.push_name }}</q-item-label>
       <q-item-label> {{ item.text }} </q-item-label>
       <q-item-label><q-btn round color="red" icon="local_grocery_store"  @click="showMessageOrderDialog(item, index)"></q-btn>
         {{item.order_descr}}
       </q-item-label>
      </q-item-section>
      <q-item-section side top>
        <div v-if="item.customer.clients.length>0">Клиент: {{ item.customer.clients[0].name }}</div>
      <q-btn round icon="face"  @click="showCustomerToClientDialog(item)"></q-btn>
      </q-item-section>
    </q-item>
  </q-list>
  <q-dialog v-model="customer_to_client_dialog">
    <q-card>
      <q-card-section>{{ this.message.customer.name }}</q-card-section>
      <q-card-section>{{ this.message.customer.number }}</q-card-section>
      <q-card-section>
        <q-select
          label="Clients"
          v-model="client"
          :options="clients"
          option-label="name"
          option-value="id"
          :option-disable="(item) => item.customers.length > 0"
      />
      </q-card-section>
      <q-card-section>
        {{ this.message.text }}
      </q-card-section>
      <q-card-actions>
        <q-btn @click="customer_to_client_dialog=false">Отмена</q-btn>
        <q-btn @click="saveCustomerToClient()">Сохранить</q-btn>
      </q-card-actions>
    </q-card>
  </q-dialog>
  <q-dialog v-model="message_order_dialog">
    <q-card>
      <q-card-section>
        {{ this.message.text }}
      </q-card-section>
      <q-card-section>
        <q-table
          :columns="columns"
          :rows="message_order"
          row-key="id"
        >
          <template v-slot:top>
            <q-btn icon="add" @click="showAddGood"></q-btn>
          </template>
          <template v-slot:body-cell-actions="props">
            <q-td :props="props">
              <q-btn icon="delete" round @click="deleteGood(props.row, props.rowIndex)"></q-btn>
              <q-btn icon="edit" round @click="editGood(props.row, props.rowIndex)"></q-btn>
            </q-td>
          </template>
        </q-table>
      </q-card-section>
      <q-card-actions>
        <q-btn @click="closeMessageOrderDialog">Закрыть</q-btn>
      </q-card-actions>
    </q-card>
  </q-dialog>
  <q-dialog v-model="good_dialog">
    <q-card>
      <q-card-section>
        <q-select
          v-model="message_order_row.good"
          :options="goods"
          option-label="name"
          option-value="id"
        >
        </q-select>
        <q-input label="Кол-во" v-model="message_order_row.quantity"></q-input>
        <q-input label="Цена" v-model="message_order_row.price"></q-input>
      </q-card-section>
      <q-card-actions>
        <q-btn @click="good_dialog=false">Отмена</q-btn>
        <q-btn @click="saveGood()">Сохранить</q-btn>
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>
<script>

import axios from 'axios';

const path = 'http://localhost:5000';

export default {
  name: 'MessagesList',
  data: () => ({
    messages: [],
    message: null,
    clients: [],
    message_order: [],
    goods: [],
    hide_o: false,
    message_order_row: {},
    message_order_row_index: 0,
    message_index: null,
    client: null,
    dialog: false,
    good_dialog: false,
    customer_to_client_dialog: false,
    message_order_dialog: false,
    message_order_idx: {},
    loaded: false,
    result: {},
    columns: [{
      name: 'id',
      label: 'id',
      field: 'id'
    }, {
      name: 'good_id',
      label: 'good_id',
      field: row => row.good.id
    }, {
      name: 'good',
      label: 'good',
      field: row => row.good.name
    }, {
      name: 'quantity',
      label: 'quantity',
      field: 'quantity',
    }, {
      name: 'price',
      label: 'price',
      field: 'price',
    },{
      name: 'actions',
      label: 'Actions'
    }]
  }),
  computed: {
    hide_orders:{
      get() {return this.hide_o;},
      set(val) {this.hide_o = val; this.getMessages()}
    }
  },
  methods: {
    async showAddGood() {
      if (this.goods.length === 0) {
        let result = await axios.get('http://localhost:5000/goods');
        this.goods = result.data;
      }
      this.message_order_row = {message_id: this.message.id};
      this.message_order_row_index = null;
      this.good_dialog = true;
    },
    async editGood(item, index) {
      let result;
      this.message_order_row_index = index;
      if (this.goods.length === 0) {
        let result = await axios.get('http://localhost:5000/goods');
        this.goods = result.data;
      }
      result = await axios.get("http://localhost:5000/message_order/"+this.message.id+"/"+item.id);
      this.message_order_row = result.data;
      this.good_dialog = true;
    },
    saveGood() {
      axios.post('http://localhost:5000/message_order', {
        message_order_row: this.message_order_row
      }).then((data) => {
        let row = data.data;
        if(this.message_order_row_index === null){
          this.message_order.push(row);
        } else {
          this.message_order[this.message_order_row_index] = row;
        }
        console.log(data.data);
      }).catch((error) => {
        console.error(error);
      });
      this.good_dialog = false;
    },
    deleteGood(row) {
      console.log("delete " + row);
    },
    itemClass(item) {
      if (item.customer && item.customer.clients.length > 0) {
        return "bg-green-1";
      } else {
        return 'bg-red-1';
      }
    },
    saveCustomerToClient() {
      axios.post('http://localhost:5000/customers_to_clients', {
        client: this.client,
        customer: this.message.customer,
      }).then((data) => {
        this.message.customer.clients = [this.client];
        console.log(data.data);
      }).catch((error) => {
        console.error(error);
      });
      this.customer_to_client_dialog = false;
    },
    async showCustomerToClientDialog(item) {
      this.message = item;
      if (item.customer.clients.length > 0) {
        this.client = item.customer.clients[0];
      } else {
        this.client = null;
      }
      if (this.clients.length !== 0) {
        this.customer_to_client_dialog = true;
      } else {
        let result = await axios.get('http://localhost:5000/clients');
        this.clients = result.data;
        this.customer_to_client_dialog = true;
      }

    },
    async closeMessageOrderDialog(){
        let result = await axios.get('http://localhost:5000/messages/'+this.message.id);
        this.messages[this.message_index] = result.data;
        this.message_order_dialog = false;
    },
    async showMessageOrderDialog(item, index) {
      this.message = item;
      this.message_index = index;
        let result = await axios.get('http://localhost:5000/message_order/'+item.id);
      this.message_order = result.data;
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
      axios.get(path + '/messages').then((res) => {
        this.messages = res.data;
      }).catch((error) => {
        console.error(error);
      });
    }
  },
  created() {
    this.getMessages();
  }
}
</script>
