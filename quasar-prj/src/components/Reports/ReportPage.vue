<template>
  <q-card>
    <q-btn
      label="Заказы"
      @click="clientGoodReport()"
    >
    </q-btn>
    <q-btn
      label="Оплаты"
      @click="clientPaymentReport()"
    >
    </q-btn>
    <q-btn
      color="teal"
    >
      <a :href="path+'/get_reports'" download>Отчет</a>
      <q-icon left size="3em" name="map"/>
    </q-btn>
  </q-card>
  <q-card class="row">
    <q-list>
      <ClientReportItem v-for="(val, key) in report.clients"
                        :key=key
                        :client="key"
                        :goods="val">
      </ClientReportItem>
    </q-list>
    <q-list>
      <ClientReportItem v-for="(val, key) in report.gs_clients"
                        :key=key
                        :client="key"
                        :goods="val">
      </ClientReportItem>
    </q-list>
  </q-card>
  <q-card>
    <q-list>
      <q-item v-for="(val,key) in report.goods"
              :key=key>
        {{ key }}{{ val }}
      </q-item>
    </q-list>
    <q-list>
      <q-item v-for="(val,key) in report.gs_goods"
              :key=key>
        {{ key }}{{ val }}
      </q-item>
    </q-list>
  </q-card>
  <q-table
    dense
    wrap-cells
    :grid="isGrid()"
    virtual-scroll
    style="max-height: 90vh"
    separator="cell"
    :rows-per-page-options="[0]"
    :rows="report"
    :columns="columns"
  >
    <template v-slot:body-cell="props">
      <q-td :props="props">
        <div
          @click="rowClick(props)">
          <q-icon v-if="props.value.comment" name="bookmark" color="red">
            <q-tooltip>
              {{ props.value.comment }}
            </q-tooltip>
          </q-icon>
          {{ props.value ? props.value.value : '' }}
        </div>
      </q-td>
    </template>
    <template v-slot:header-cell="props">
      <q-th :props="props" @click="rowClick(props)">
        <div>
          <q-icon v-if="props.col.good_id && !props.col.active" name="bookmark" color="red"/>
          {{ props.col.name }}
        </div>
      </q-th>
    </template>
    <template v-slot:item="props">
      <q-card class="col-xs-12 col-sm-6 col-lg-3 col-xl-3">
        <q-list dense @click="rowClick(props)">
          <q-item v-for="col in props.cols.filter(col => !!col.value.value)" :key="col.name">
            <q-item-section>
              <q-item-label caption :class="(col.good_id && !col.active) ? 'text-red-8' : ''">{{ col.label }}</q-item-label>
            </q-item-section>
            <q-item-section side>
              <q-item-label>
          <q-icon v-if="col.value.comment" name="bookmark" color="red">
            <q-tooltip>
              {{ col.value.comment }}
            </q-tooltip>
          </q-icon>
                {{ col.value.value }}
              </q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </q-card>
    </template>
  </q-table>
  <good-dialog v-model="good_dialog" :good="good" @close="good_dialog=false"></good-dialog>
  <q-dialog v-model="itog_dialog">
    <q-card>
      <q-table
        :rows="itog.data" @row-click="itogDialogClick"></q-table>
      {{ itog.customer.name }}
      <q-input
        debounce="1000"
        :model-value="send_text"
        type="textarea"
        autogrow/>
      <q-card-actions>
        <img v-if="itog.customer.params && ((itog.customer.params.from || '') ==='telegram')" src="icons/telegram.svg" height="32" width="32"/>
        <q-btn @click="itog_dialog=false">Close</q-btn>
        <q-btn @click="send()">Send</q-btn>
      </q-card-actions>
    </q-card>
  </q-dialog>
  <message-order-dialog v-model="message_order_dialog" :message="message" @close="message_order_dialog=false"/>
</template>

<script>
// import { useQuasar } from 'quasar'
import axios from "axios";
import {parseReport} from "./parse_report";
import ClientReportItem from "components/Reports/ClientReportItem.vue";
import GoodDialog from "components/Messages/GoodDialog.vue";
import {Goods, Message} from "src/store/berries_store/models";
import MessageOrderDialog from "components/Messages/MessageOrderDialog.vue";

const path = process.env.API_URL;

export default {
  name: "ReportPage",
  components: {GoodDialog, ClientReportItem, MessageOrderDialog},
  data: () => ({
    // $q: useQuasar(),
    report: [],
    columns: [],
    path: path,
    good_dialog: false,
    itog_dialog: false,
    itog: {},
    good: {},
    message_order_dialog: false,
    message: {},
    send_text: '',
    dates_params: ''//'?start_date=14.06.2024&end_date=25.06.2024'
  }),
  methods: {
    send(a, b, c) {
      axios.post(path + "/send", {customer: this.itog.customer.id, text: this.send_text});
    },
    rowClick(props) {
      if (!props.row) {
        //заголовок
        axios.get(path + '/goods/' + props.col.good_id+this.dates_params).then((res) => {
          this.good = new Goods(res.data);
          this.good_dialog = true;
        }).catch((error) => {
          console.error(error);
        });
        return;
      }
      const client_id = props.row.name.client_id;
      const cell = props.col ? props.row[props.col.name] : {};
      if (cell.good_id) {
        //на клетку с кол-вом
        axios.get(path + '/get_orders/' + client_id + '/' + cell.good_id+this.dates_params).then((res) => {
           debugger
          this.itog = res.data;
          this.itog_dialog = true;
        }).catch((error) => {
          console.error(error);
        });
      } else {
        //на клетку с клиентом
        axios.get(path + '/get_orders/' + client_id+this.dates_params).then((res) => {
          this.itog = res.data;
          this.send_text = 'Добрый день!\n' +
            'Сумма за ягоды из Сербии - \n' +
            this.itog.sum +
            '\nЗаказ: \n'+
            this.itog.order+
            '\nОплата по реквизитам сбербанк 2202200785632462 или\n' +
            'по номеру телефона +79191084711\n' +
            ' Без комментариев к платежу , чек мне в лс. НЕТ ЧЕКА = нет оплаты\n' +
            'Получатель: Наталья Владимировна Р\n'+
            'Оплата до 15:00 28 июня '
          this.itog_dialog = true;
        }).catch((error) => {
          console.error(error);
        });
      }
    },
    async itogDialogClick(event, row) {
      await Message.api().get('messages/' + row.id, {
        persistBy: 'create',
        persistOptions: {
          insertOrUpdate: ['customer', 'clients']
        }
      });
      this.message = Message.query().where('id', row.id).with('for_client').with('customer').with('customer.clients').get()[0];
      this.message_order_dialog = true;
    },
    compareReport() {
      axios.get(path + '/compare_reports').then((res) => {
        this.report = res.data;
      }).catch((error) => {
        console.error(error);
      });
    },
    isGrid() {
      return this.$q.screen.xs;
    },
    async clientGoodReport() {
      await Goods.api().get('goods')
      const res = await axios.get(path + '/client_good_report'+this.dates_params);
      const rep = parseReport(res.data);
      this.columns = rep.columns;
      this.report = rep.rows
      // this.report = res.data;
    },
    clientPaymentReport() {
      axios.get(path + '/client_payment_report').then((res) => {
        this.report = res.data;
      }).catch((error) => {
        console.error(error);
      });
    },
    getReport() {
      axios.get(path + '/get_reports').then((res) => {
        this.report = res.data;
      }).catch((error) => {
        console.error(error);
      });
    }
  },
  created() {
    // this.getReport()
  }
}
</script>

<style scoped>

</style>
