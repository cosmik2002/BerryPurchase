<template>
  <q-file v-model="file" label="Sber Statement"/>
  <q-btn @click="fileUpload($event)">Upload</q-btn>
  <q-btn @click="parseNotify($event)">Parse Notifications</q-btn>
  <div>{{upload_result}}</div>
  <q-list>
    <q-item v-for="item in Payments"
                 :key="item.id" v-ripple:red>
      <q-item-section>

        <q-item-label v-if="item.payer"> {{ item.payer.name }}~~{{ item.payer.card_number}} </q-item-label>
        <q-item-label>{{ item.timestamp }} {{ item.sum }} {{item.operation_code}}{{item.sms_id}} {{ item.comment }}</q-item-label>
      </q-item-section>

    </q-item>
  </q-list>
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
    client: [],
    dialog: false,
    title: 'null',
    loaded: false,
    upload_result: ''
  }),
  methods:  {
    parseNotify(evt) {
      this.upload_result = '';
        axios.get('http://localhost:5000/parse_notify').then((data) =>{
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
            console.log(data.data);
        })
        .catch(function (err) {
            console.log('FAILURE!!'+err);
        });
    },
    getPayments() {
      const path = 'http://localhost:5000';
      axios.get(path+'/payments').then((res)=>{
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
