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
  <div class="pagination">
    <q-btn class="parev_page" v-if="page>1" @click="page--; getPayments()">Prev</q-btn>
    <div class="page_number"> {{ page }}</div>
    <q-btn class="next_page" @click="page++; getPayments()">Next</q-btn>
  </div>
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
    page: 1,
    page_size: 10
  }),
  computed:{
    payments () {
        return Payment.query().with('payer').with('payer.clients').all();
    },
    search:{
      get() {
        return this.src;
      },
      set(val) {
        this.src = val;
        this.getPayments();
        console.log(val);
      }
    }
  },
  components: {
      'payment-c': PaymentItem,
    PayerToClientDialog

  },
  methods: {
    getPayments() {
        let url = 'payments';
        let params = '';
        if (this.search)
          params += `search=${this.src}`;
        params += (params !== '' ? '&' : '') + `page=${this.page}`;
        params += (params !== '' ? '&' : '') + `page_size=${this.page_size}`;
        url += '?' + params;
        Payment.api().get(url, { persistBy: 'create' });
    },
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
      axios.get('parse_notify').then((data) => {
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
      axios.post('file_save',
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
    this.getPayments();
  }

}
</script>

<style scoped>
.pagination {
  display: flex;
  flex-wrap: wrap;
}
.page_number {
  padding: 10px;
}
</style>
