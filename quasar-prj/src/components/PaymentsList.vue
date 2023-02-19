<template>
  <q-file v-model="file" label="Файл выписки"/>
  <q-btn @click="fileUpload($event)">Загрузить выписку</q-btn>
  <q-btn @click="parseNotify($event)">Разобрать уведомления</q-btn>
  <div>{{ upload_result }}</div>
  <q-list>
    <q-item v-for="item in Payments"
            :key="item.id" v-ripple:red clickable @click="editPayer(item)" :class="itemClass(item)">
      <q-item-section >
        <q-item-label v-if="item.payer">
          <div>Плательщик: {{ item.payer.name }}</div>
          <div>Карта: {{ item.payer.card_number }}</div>
        </q-item-label>
        <q-item-label>{{ item.timestamp }} {{ item.sum }} {{ item.operation_code }}{{ item.sms_id }} {{
            item.comment
          }}
        </q-item-label>
      </q-item-section>
      <q-item-section side top>
        <q-item-label v-if="item.payer && item.payer.clients.length > 0">
          <div>Клиент: {{ item.payer.clients[0].name }}</div>
        </q-item-label>
      </q-item-section>
    <q-separator/>
    </q-item>
  </q-list>
  <q-dialog v-model=
              "dialog" scrollable max-width="30%">
    <q-card style="min-width: 300px">
      <q-card-section>
      <q-card-section>
        <div>Плательщик</div>
        <div>{{this.payment.payer.name}}</div>
        <div>{{this.payment.payer.card_number}}</div>
      </q-card-section>
        <q-select
          label="Clients"
          v-model="client"
          :options="clients"
          option-label="name"
          option-value="id"/>
      </q-card-section>
      <q-card-actions>
        <q-btn @click="dialog=false">Отмена</q-btn>
        <q-btn @click="savePayerToClient()">Сохранить</q-btn>
      </q-card-actions>
    </q-card>
  </q-dialog>

</template>
<script>

import axios from 'axios';

const path = 'http://localhost:5000';

export default {
  name: 'PaymentsList',
  data: () => ({
    file: null,
    Payments: [],
    clients: [],
    client: null,
    payment: null,
    dialog: false,
    title: 'null',
    loaded: false,
    upload_result: ''
  }),
  methods: {
    itemClass(item){
      if (item.payer && item.payer.clients.length > 0) {
        return "bg-green-1";
      } else {
        return 'bg-red-1';
      }
    },
    savePayerToClient() {
      axios.post('http://localhost:5000/payers_to_clients', {
        client: this.client,
        payer: this.payment.payer
      }).then((data) => {
        this.payment.payer.clients = [this.client];
        console.log(data.data);
      }).catch((error) => {
        console.error(error);
      });
      console.log(this.payment.payer);
      console.log(this.client);
      this.dialog = false;
    },
    editPayer(item) {
      this.payment = item;
      if (item.payer.clients.length > 0) {
        this.client = item.payer.clients[0];
      } else {
        this.client = null;
      }
      if (this.clients.length !== 0) {
        this.dialog = true;
      } else {
        axios.get('http://localhost:5000/clients').then((data) => {
          this.clients = data.data;
          this.dialog = true;
        }).catch((error) => {
          console.error(error);
        });

      }
      console.log(item.payer.name);
    },
    parseNotify(evt) {
      this.upload_result = '';
      axios.get('http://localhost:5000/parse_notify').then((data) => {
        this.upload_result = data.data;
      }).catch((error) => {
        console.error(error);
      });

    },

    fileUpload(file) {
      this.upload_result = '';
      const me = this;
      const formData = new FormData();
      formData.append('file', this.file);
      axios.post('http://localhost:5000/file_save',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      ).then(function (data) {
        me.upload_result = data.data;
        this.file = null;
        console.log(data.data);
      })
        .catch(function (err) {
          console.log('FAILURE!!' + err);
        });
    },
    getPayments() {
      const path = 'http://localhost:5000';
      axios.get(path + '/payments').then((res) => {
        this.Payments = res.data;
      }).catch((error) => {
        console.error(error);
      });
    }
  },
  created() {
    this.getPayments();
  }
}
</script>
