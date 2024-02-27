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
    <q-icon left size="3em" name="map" />
  </q-btn>
    </q-card>
<q-card class="row">
  <q-list>
    <ClientReportItem v-for="(val, key) in report.clients"
            :key = key
    :client="key"
    :goods="val">
    </ClientReportItem>
  </q-list>
  <q-list>
    <ClientReportItem v-for="(val, key) in report.gs_clients"
            :key = key
    :client="key"
    :goods="val">
    </ClientReportItem>  </q-list>
</q-card>
<q-card>
  <q-list>
    <q-item v-for="(val,key) in report.goods"
            :key = key>
      {{key}}{{val}}
    </q-item>
  </q-list>
  <q-list>
    <q-item v-for="(val,key) in report.gs_goods"
            :key = key>
      {{key}}{{val}}
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
  >
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
</template>

<script>
// import { useQuasar } from 'quasar'
import axios from "axios";
import {parseReport} from "./parse_report";
import ClientReportItem from "components/Reports/ClientReportItem.vue";
const path = process.env.API_URL;

export default {
  name: "ReportPage",
  components: {ClientReportItem},
  data: () => ({
    // $q: useQuasar(),
    report:[],
    path: path
  }),
  methods:{
    compareReport(){
      axios.get(path + '/compare_reports').then((res) => {
        this.report = res.data;
      }).catch((error) => {
        console.error(error);
      });
    },
    isGrid(){
      return this.$q.screen.xs;
    },
    clientGoodReport(){
      axios.get(path + '/client_good_report').then((res) => {
        this.report =parseReport(res.data);
        // this.report = res.data;
      }).catch((error) => {
        console.error(error);
      });
    },
    clientPaymentReport(){
      axios.get(path + '/client_payment_report').then((res) => {
        this.report = res.data;
      }).catch((error) => {
        console.error(error);
      });
    },
    getReport(){
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
