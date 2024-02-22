<template>
  <q-card>
  <q-btn
    color="teal"
    label="Итог"
    @click="itogReport()"
    >
    <q-icon left size="3em" name="map" />
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
  :rows="report"
  >
  </q-table>
</template>

<script>
import axios from "axios";
import ClientReportItem from "components/Reports/ClientReportItem.vue";
const path = process.env.API_URL;

export default {
  name: "ReportPage",
  components: {ClientReportItem},
  data: () => ({
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
    itogReport(){
      axios.get(path + '/itog_report').then((res) => {
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
