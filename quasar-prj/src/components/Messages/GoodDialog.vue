<template>
  <q-dialog>
    <q-card>
      <q-card-section>
        <q-select
          v-model="message_order_row.good"
          :options="goods"
          option-label="name"
          option-value="id"
        >
        </q-select>
        <q-input label="Кол-во" v-model="message_order_row.quantity"></q-input>
        <q-input label="Цена" v-model="message_order_row.price"></q-input>
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

export default {
  name: "GoodDialog",
  props: {
    row: {
      good:{}
    }
  },
  emits: ['close'],
  data: () => ({
    message_order_row: {
    }
  }),
  computed: {
    goods() {
      return Goods.query().all();
    }
  },
  methods: {
    saveGood() {
      MessageOrder.api().post('message_order', {
        id: this.message_order_row.id,
        message_id: this.message_order_row.message_id,
        good_id: this.message_order_row.good.id,
        quantity: this.message_order_row.quantity,
        price: this.message_order_row.price,
      });
      this.$emit('close');
    },
    getGoods() {
      Goods.api().get('goods');
    }
  },
  beforeUpdate() {
    this.message_order_row = this.row;
    this.getGoods();
  }
}
</script>

<style scoped>

</style>
