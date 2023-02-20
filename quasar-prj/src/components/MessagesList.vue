<template>
  <q-btn @click="startWaClient()">Запустить Watsapp</q-btn>
  <q-btn @click="loadMessages()">Load Messages</q-btn>
  <div>{{ result }}</div>
  <q-list separator>
    <q-item v-for="item in messages"
            :key="item.id" clickable @click="showMessageDialog(item)" v-ripple:red :class="itemClass(item)">
      <q-item-section>
        <q-item-label>{{ item.customer.number }}</q-item-label>
        <q-item-label>{{ item.customer.push_name }}</q-item-label>
        <q-item-label>{{ item.text }}</q-item-label>
      </q-item-section>
      <q-item-section v-if="item.customer.clients.length>0" side top>
        <div>Клиент: {{ item.customer.clients[0].name }}</div>
      </q-item-section>
    </q-item>
  </q-list>
  <q-dialog v-model="dialog">
    <q-card>
      <q-card-section>{{ this.message.customer.number }}</q-card-section>
      <q-card-section>
        <q-select
          label="Clients"
          v-model="client"
          :options="clients"
          option-label="name"
          option-value="id"/>
      </q-card-section>
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
              <q-btn icon="delete" @click="deleteGood(props.row)"></q-btn>
            </q-td>
          </template>
        </q-table>
      </q-card-section>
      <q-card-actions>
        <q-btn @click="dialog=false">Отмена</q-btn>
        <q-btn @click="saveCustomerToClient()">Сохранить</q-btn>
      </q-card-actions>
    </q-card>
  </q-dialog>
  <q-dialog v-model="good_dialog">
    <q-card>
      <q-card-section>
        <q-select
          v-model="good"
          :options="goods"
          option-label="name"
          option-value="id"
        >
        </q-select>
      </q-card-section>
      <q-card-actions>
        <q-btn @click="good_dialog=false">Отмена</q-btn>
        <q-btn @click="addGood()">Добавить</q-btn>
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
    good: null,
    client: null,
    dialog: false,
    good_dialog: false,
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
      field: 'quantity'
    }, {
      name: 'price',
      label: 'price',
      field: 'price'
    }]
  }),
  methods: {
    showAddGood() {
      this.good_dialog = true;
    },
    addGood() {
      this.message_order.push(
        {
          good: this.good,
          good_id: this.good.id,
          message_id: this.message.id,
          quantity: 0,
          price: 1
        }
      );
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
        message_order: this.message_order
      }).then((data) => {
        this.message.customer.clients = [this.client];
        console.log(data.data);
      }).catch((error) => {
        console.error(error);
      });
      this.dialog = false;
    },
    async showMessageDialog(item) {
      this.message = item;
      if (item.customer.clients.length > 0) {
        this.client = item.customer.clients[0];
      } else {
        this.client = null;
      }
      if (item.message_order && item.message_order.length > 0) {
        this.message_order = item.message_order;
      } else {
        this.message_order = [];
      }
      if (this.clients.length !== 0) {
        this.dialog = true;
      } else {
        let result = await axios.get('http://localhost:5000/clients');
        this.clients = result.data;
        result = await axios.get('http://localhost:5000/goods');
        this.goods = result.data;
        this.dialog = true;
      }
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
