<template>
  <q-item>
    <q-input v-model="setting.name" dense></q-input>
    <q-input v-model="setting.value" dense></q-input>
    <q-btn @click="saveItem" icon="done"></q-btn>
    <q-btn @click="delRow" icon="delete"></q-btn>
  </q-item>
</template>

<script>
import {Setting} from "src/store/berries_store/models";

export default {
  name: "SettingItem",
  props: ['item'],
  data: () => ({
    setting: {}
  }),
  methods: {
    saveItem() {
      if (!parseInt(this.setting.id)) {
        delete this.setting.id;
      }
      if (this.setting.value !== this.item.value || this.setting.name !== this.item.name) {
        Setting.api().post('settings', this.setting).then((result) => {
          this.setting = result.entities.settings[0];
        });
      }
    },
    delRow() {
      Setting.api().delete("settings/" + this.setting.id, {delete: this.setting.id});
    },
  },
  mounted() {
    this.setting = this.item.$toJson();
  }
}
</script>
<style scoped>

</style>
