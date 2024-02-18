<template>
  <q-dialog>
    <q-card>
      <q-card-section>
        <q-input label="Название" v-model="upd_good.name"></q-input>
        <q-input label="Цена" v-model="upd_good.price"></q-input>
        <q-input label="Кор. назв." v-model="upd_good.short_name"></q-input>
        <q-input label="Варианты" v-model="upd_good.variants"></q-input>
      </q-card-section>
      <q-card-actions>
        <q-btn @click="$emit('close')">Отмена</q-btn>
        <q-btn @click="saveGood()">Сохранить</q-btn>
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script>
import {Goods, MessageOrder} from "src/store/berries_store/models";
import GoodItem from "components/Messages/GoodItem.vue";
export default {
  name: "GoodDialog",
  props: {
    good: {}
  },
  emits: ['close'],
  data: () => ({
    upd_good: {},
    goodSearch:'',
    page: 1,
    page_size: 5
  }),
  methods: {
    saveGood() {
      Goods.api().post('goods', this.upd_good);
      this.$emit('close');
    },
  },
  beforeUpdate() {
    if(this.good) {
      this.upd_good = this.good.$toJson();
    }
  }
}
</script>
<style scoped>
</style>
