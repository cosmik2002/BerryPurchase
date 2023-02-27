<template>
  <q-file v-model="file" label="Файл выписки"/>
  <q-btn @click="fileUpload($event)">Загрузить выписку</q-btn>
  <q-btn @click="parseNotify($event)">Разобрать уведомления</q-btn>
  <div>{{ upload_result }}</div>
      <q-input
        v-model="search"
        debounce="1000"
        filled
        placeholder="Поиск"
        hint="Поиск по карте, сумме, имени"
      >
        <template v-slot:append>
          <q-icon name="search" />
        </template>
      </q-input>
  <q-list>
    <payment-c
    v-for="item in payments"
    :key="item.id"
    :item="item"
    v-ripple:red
    clickable
    @click="editPayer(item)"
    :class="itemClass(item)"
    >
    </payment-c>
  </q-list>
<payer-to-client-dialog
  :payment="payment"
  v-model="dialog"
  @close="dialog=false">
</payer-to-client-dialog>
</template>
<script>

import axios from 'axios';
import PaymentItem from 'components/Payments/PaymentItem.vue'
import Payment from "src/store/berries_store/models/Payments";
import PayerToClientDialog from "components/Payments/PayerToClientDialog.vue";

export default {
  name: 'PaymentsList',
  data: () => ({
    file: null,
    payment: null,
    dialog: false,
    upload_result: '',
    src: '',
  }),
  computed:{
    payments () {
      if (this.src) {
        let p = Payment.query().with('payer').whereHas('payer', (query) => {
          query.where((payer) =>
          !!payer.card_number && payer.card_number.indexOf(this.src) !== -1
        )
        }).with('payer.clients').all();
        return p;
      } else {
        return Payment.query().with('payer').with('payer.clients').all();
      }
    },
    search:{
      get() {
        return this.src;
      },
      set(val) {
        this.src = val;
/*        this.payments = Payment.query().with('payer', (query) => {
          query.where((payer) => {
          payer.card_number && payer.card_number.indexOf(val) !== -1
        })
        }).with('payer.clients').all();*/
        console.log(val);
      }
    }
  },
  components: {
      'payment-c': PaymentItem,
    PayerToClientDialog

  },
  methods: {
    itemClass(item){
      if (item.payer && item.payer.clients.length > 0) {
        return "bg-green-1";
      } else {
        return 'bg-red-1';
      }
    },

    editPayer(item) {
      this.payment = item;
      this.dialog = true;
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
  },
  mounted() {
    Payment.api().get('http://localhost:5000/payments');
  }

}
</script>
