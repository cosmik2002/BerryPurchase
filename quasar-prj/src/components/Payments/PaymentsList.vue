<template>
  <div>{{ upload_result }}</div>
  <q-input v-model="beg_sum"
           debounce="1000"
           placeholder="Сумма на начало">
  </q-input>
  <q-input filled
           v-model="start_date"
           mask="date"
           debounce="1000"
           :rules="['date']">
    <template v-slot:append>
      <q-icon name="event" class="cursor-pointer">
        <q-popup-proxy cover transition-show="scale" transition-hide="scale">
          <q-date v-model="start_date">
            <div class="row items-center justify-end">
              <q-btn v-close-popup label="Close" color="primary" flat/>
            </div>
          </q-date>
        </q-popup-proxy>
      </q-icon>
    </template>
  </q-input>
  <q-input
    v-model="search"
    debounce="1000"
    filled
    placeholder="Поиск"
    hint="Поиск по карте, сумме, имени"
  >
    <template v-slot:append>
      <q-icon name="search"/>
    </template>
  </q-input>
  <q-list separator>
    <payment-c
      v-for="item in payments"
      :key="item.id"
      :item="item"
      v-ripple:red
      clickable
      @click="editPayer(item)"
      :is-ost="!!beg_sum"
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

import PaymentItem from 'components/Payments/PaymentItem.vue'
import Payment from "src/store/berries_store/models/Payments";
import PayerToClientDialog from "components/Payments/PayerToClientDialog.vue";

export default {
  name: 'PaymentsList',
  data: () => ({
    payment: null,
    dialog: false,
    upload_result: '',
    beg_sum: '',
    start_date_: '',
    src: '',
    page: 1,
    page_size: 25
  }),
  computed: {
    start_date: {
      get() {
        return this.start_date_
      },
      set (val) {
        this.start_date_ = val;
        this.getPayments();
      }
    },
    payments() {
      let query = Payment.query();
      let payments = query.with('payer').with('payer.clients').orderBy('timestamp', 'desc').all();
      let ost = parseFloat(this.beg_sum);
      payments = payments.map((payment) => {
        let data = payment.$toJson();
        data.ost = (data.ost) + ost;
        return data;
      })
      return payments
    },
    search: {
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
      if (this.start_date_) {
        params += (params !== '' ? '&' : '') + `start_date=${this.start_date_}`;
      }
      if (this.beg_sum) {
        params += (params !== '' ? '&' : '') + `beg_sum=${this.beg_sum}`;
      }
      url += '?' + params;
      Payment.api().get(url, {persistBy: 'create'});
    },
    itemClass(item) {
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
