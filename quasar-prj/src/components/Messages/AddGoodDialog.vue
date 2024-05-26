<template>
  <q-dialog @show="show">
    <q-card>
      <q-card-section>
<!--        <q-list>
          <good-item v-for="good in goods"
                     :key="good.id"
                     :good="good">

          </good-item>
        </q-list>-->
<!--        <div class="pagination">
          <div v-if="page>0" @click="page&#45;&#45;" style="cursor: pointer">prev</div>
          <div>{{page}}</div>
          <div @click="page++" style="cursor: pointer">next</div>
        </div>-->
        <q-select
          v-model="message_order_row.good"
          :options="goods"
          option-label="name"
          option-value="id"
                    use-input
          @filter="filterGood"
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
import GoodItem from "components/Messages/GoodItem.vue";
export default {
  name: "AddGoodDialog",
  props: {
    row: {
      good:{}
    }
  },
  emits: ['close'],
  data: () => ({
    message_order_row: {},
    goodSearch:'',
    page: 1,
    page_size: 5
  }),
  components:{
   // GoodItem
  },
  computed: {
    goods() {
      if (this.goodSearch === '') {
        return Goods.query().orderBy('name').all();
      } else {
        let val = this.goodSearch.toLocaleLowerCase();
        return Goods.query().where((good) => good.name.toLocaleLowerCase().indexOf(val) > -1).orderBy('name').all();
      }
    }
  },
  methods: {
    filterGood(val, update){
      update(()=>{this.goodSearch = val;})
    },
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
    },
    show(){
      this.message_order_row = this.row;
      this.getGoods();

    }
  },
}
</script>

<style scoped>
.pagination {
  display: flex;
  flex-wrap: wrap;
}
</style>
