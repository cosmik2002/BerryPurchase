<template>
    <q-btn @click="startWaClient()">Запустить Watsapp</q-btn>
  <q-btn @click="loadMessages()">Load Messages</q-btn>
  <q-btn @click="waLogout()">waLogout</q-btn>
  <q-btn @click="waLogin()">waLogin</q-btn>
  <q-btn @click="fillPayments">fillPayments</q-btn>
  <q-btn @click="getSummary">getSummary</q-btn>
    <q-btn @click="sockSend">sockSend</q-btn>
  <q-file v-model="file" label="Файл выписки"/>
  <q-btn @click="fileUpload($event)">Загрузить выписку</q-btn>
  <q-btn @click="parseNotify($event)">Разобрать уведомления</q-btn>
  <q-btn @click="getPriceList">getPriceList</q-btn>
  <q-separator/>
  <q-btn @click="zenMoney"><img src="~assets/zen_money.svg" alt="zen money" style="width:100px"/></q-btn>
  <q-separator/>
  <q-btn @click="addRow" icon="add"></q-btn>
  <q-list>
    <setting-item v-for="item in settings" :key="item.id" :item="item"></setting-item>
  </q-list>
  <div v-for="(val,key) in upload_result" :key=key>
    <div v-if="key==='errors'">
      <div v-for="(msg, index) in val" :key="index">
        {{msg}}
      </div>
      </div>
    <div v-else>
    {{key}}:{{val}}
      </div>
  </div>
  <itog-report :report_data="report"/>
  <canvas height='320' width='480' id='canvas'></canvas>
</template>

<script>
import SettingItem from "components/Settings/SettingItem.vue";
import ItogReport from "components/Settings/ItogReport.vue";
import {Setting} from "src/store/berries_store/models";
import axios from "axios";
import QRCode from "qrcode";

const path = process.env.API_URL;

export default {
  name: "SettingsPage",
  data: () => ({
    file: null,
    report: null,
    socket: null,
    upload_result: ''
  }),
  components: {
    SettingItem,
    ItogReport
  },
  computed: {
    settings() {
      return Setting.all();
    }
  },
  methods: {
    parseNotify(evt) {
      this.upload_result = '';
      axios.get(path + '/parse_notify').then((data) => {
        this.upload_result = data.data;
      }).catch((error) => {
        console.error(error);
      });
    },
    getPriceList(evt) {
      this.upload_result = '';
      axios.get(path + '/get_price_list').then((data) => {
        this.upload_result = data.data;
      }).catch((error) => {
        console.error(error);
      });
    },
    zenMoney(evt) {
      this.upload_result = '';
      axios.get(path + '/zen_money').then((data) => {
        this.upload_result = data.data;
      }).catch((error) => {
        console.error(error);
      });
    },
    getSummary(evt) {
      this.upload_result = '';
      axios.get(path + '/get_summary').then((data) => {
        this.report = data.data;
      }).catch((error) => {
        console.error(error);
      });
    },
    fileUpload(file) {
      this.upload_result = '';
      const me = this;
      const formData = new FormData();
      formData.append('file', this.file);
      axios.post(path + '/file_save',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      ).then(function (data) {
        me.upload_result = data.data;
        // me.file = null;
        console.log(data.data);
      })
        .catch(function (err) {
          console.log('FAILURE!!' + err);
        });
    },
    getSettings() {
      let url = 'settings';
      Setting.api().get(url, {persistBy: 'create'});
    },

    addRow() {
      Setting.insert({data: {name: '', value: ''}}).then((res)=>{
        let t=res;
      });
    },

    fillPayments() {
      axios.get(path + '/fill_payments')
    },
waLogout() {
      axios.get(path + '/wa_logout')
},
waLogin() {
      axios.get(path + '/wa_login').then((res)=>{
        this.subscribe();
      });
},
    startWaClient() {
      axios.get(path + '/start_wa_client').then((res) => {
        this.result = res.data;
        this.subscribe();
      }).catch((error) => {
        console.error(error);
      });
    },

    subscribe() {
      axios.get(path + '/subscribe').then((res) => {
        if (res.data.qrcode) {
          var canvas = document.getElementById('canvas')
          QRCode.toCanvas(canvas, res.data.qrcode, function (error) {
            if (error) console.error(error)
            console.log('success!');
          });
          return
        }
        console.log(res.data.status)
        if (res.data.status == 1) {
          setTimeout(this.subscribe, 1000);
        } else if (res.data.status == 2){
          this.upload_result = {status: 'wa started'};
        }
      }).catch((error) => {
        console.log(error);
      });
    },
    loadMessages() {
      axios.get(path + '/load_messages').then((res) => {
        this.upload_result=res.data;
      }).catch((error) => {
        console.error(error);
      });
    },
    startWebSocket() {
    this.socket = new WebSocket('ws://127.0.0.1:5000/echo');
      this.socket.addEventListener('message', ev => {
        console.log('<<< ' + ev.data);
      });
    },
    sockSend() {
      this.socket.send("ping");
    }
  },
  mounted() {
    this.getSettings();
    this.startWebSocket();
    this.subscribe();
  }
}
</script>

<style scoped>

</style>
