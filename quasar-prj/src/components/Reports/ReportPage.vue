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
          {{ props.col.name }}
        </div>
      </q-th>
    </template>
    <template v-slot:item="props">
      <q-card class="col-xs-12 col-sm-6 col-lg-3 col-xl-3">
        <q-list dense>
          <q-item v-for="col in props.cols.filter(col => !!col.value)" :key="col.name">
            <q-item-section>
              <q-item-label caption>{{ col.label }}</q-item-label>
            </q-item-section>
            <q-item-section side>
              <q-item-label>{{ col.value }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </q-card>
    </template>
  </q-table>
  <good-dialog v-model="good_dialog" :good="good" @close="good_dialog=false"></good-dialog>
<q-dialog v-model="itog_dialog">
  <q-table
  :rows="itog"/>
</q-dialog>
</template>

<script>
// import { useQuasar } from 'quasar'
import axios from "axios";
import {parseReport} from "./parse_report";
import ClientReportItem from "components/Reports/ClientReportItem.vue";
import GoodDialog from "components/Messages/GoodDialog.vue";
import {Goods} from "src/store/berries_store/models";

const path = process.env.API_URL;

export default {
  name: "ReportPage",
  components: {GoodDialog, ClientReportItem},
  data: () => ({
    // $q: useQuasar(),
    report: [],
    columns: [],
    path: path,
    good_dialog: false,
    itog_dialog: false,
    itog:[],
    good: {}
  }),
  methods: {
    rowClick(props) {
      if (!props.row) {
        //заголовок
        axios.get(path + '/goods/' + props.col.good_id).then((res) => {
          this.good = new Goods(res.data) ;
          this.good_dialog = true;
        }).catch((error) => {
          console.error(error);
        });
        return;
      }
      const client_id = props.row.name.client_id;
      const cell = props.row[props.col.name]
      if (cell.good_id) {
        //на клеку с кол-вом
        axios.get(path + '/get_orders/' + client_id + '/' + cell.good_id).then((res) => {
          this.itog = res.data;
          this.itog_dialog = true;
        }).catch((error) => {
          console.error(error);
        });
      } else {
        //на клетку с клиентом
        axios.get(path + '/get_orders/' + client_id).then((res) => {
          this.itog = res.data;
          this.itog_dialog = true;
        }).catch((error) => {
          console.error(error);
        });
      }
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
    clientGoodReport() {
      axios.get(path + '/client_good_report').then((res) => {
        const rep = parseReport(res.data);
       this.columns = rep.columns;
        this.report = rep.rows
        // this.report = res.data;
      }).catch((error) => {
        console.error(error);
      });
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
