<template>
    <q-btn @click="startWaClient()">Запустить Watsapp</q-btn>
  <q-btn @click="loadMessages()">Load Messages</q-btn>
  <q-btn @click="fillPayments">fillPayments</q-btn>
  <q-file v-model="file" label="Файл выписки"/>
  <q-btn @click="fileUpload($event)">Загрузить выписку</q-btn>
  <q-btn @click="parseNotify($event)">Разобрать уведомления</q-btn>
  <q-separator/>
  <q-btn @click="addRow" icon="add"></q-btn>
  <q-list>
    <setting-item v-for="item in settings" :key="item.id" :item="item"></setting-item>
  </q-list>
</template>

<script>
import SettingItem from "components/Settings/SettingItem.vue";
import {Setting} from "src/store/berries_store/models";
import axios from "axios";

const path = process.env.API_URL;

export default {
  name: "SettingsPage",
  data: () => ({
    file: null,
  }),
  components: {
    SettingItem
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
        this.file = null;
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
      Setting.insert({data: {name: '', value: ''}});
    },
    fillPayments() {
      axios.get(path + '/fill_payments')
    },
    startWaClient() {
      axios.get(path + '/start_wa_client').then((res) => {
        this.result = res.data;
      }).catch((error) => {
        console.error(error);
      });
    },
    loadMessages() {
      axios.get(path + '/load_messages').then((res) => {
        this.result = res.data;
      }).catch((error) => {
        console.error(error);
      });
    }
  },
  mounted() {
    this.getSettings();
  }
}
</script>

<style scoped>

</style>
