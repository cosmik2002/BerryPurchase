<template>
  <q-table
    :columns="columns"
    :rows="goods"
    virtual-scroll
    style="max-height: 90vh"
    v-model:pagination="pagination"
    :rows-per-page-options="[0]"
  >
          <template v-slot:body="props">
            <q-tr :props="props">
              <q-td v-for="col in columns"
                    :key="col.name"
                    :props="props">
               <span v-if="col.name==='url'">
                <a :href="props.row[col.name]" target="_blank">link</a>
               </span>
               <span v-else-if="col.name==='image'">
<!--                <img :src="props.row[col.name]"/>-->
               </span>
                <span v-else-if="col.name==='price' || col.name==='org_price'">
                   <q-input
                     dense
                     debounce="1000"
                     :model-value="props.row[col.name] ? parseInt(props.row[col.name]) : ''"
                     @update:model-value="updRow(props.row, {[col.name]: $event})">
                   </q-input>

               </span>
                <span v-else-if="col.name==='variants' || col.name==='type'">
                   <q-input
                     dense
                     debounce="1000"
                     :model-value="props.row[col.name]"
                     @update:model-value="updRow(props.row, {[col.name]: $event})">
                   </q-input>
               </span>
                <span v-else-if="col.name==='active'">
                  <q-checkbox
                    label=""
                  :model-value="props.row['active']"
                   @update:model-value="updRow(props.row, {active: $event})">
                  </q-checkbox>
                </span>
                <span v-else>{{ props.row[col.name] }}</span>
              </q-td>
            </q-tr>
          </template>
  </q-table>
</template>

<script>
import {Goods, MessageOrder} from
    "src/store/berries_store/models";
import axios from "axios";

const path = process.env.API_URL;

export default {
  name: "GoodsPage",
  data: () => ({
    pr: null,
    columns: [
      {
        name: 'name',
        label: 'Название',
        style: 'width: 40%',
        align: 'left',
        field: 'name'
      }, {
        name: 'price',
        label: 'Цена',
        field: 'price',
      },
      {
        name: 'active',
        label: 'Активно',
        field: 'active',
      }, {
        name: 'variants',
        label: 'Слова',
        field: 'variants',
      }, {
        name: 'org_price',
        label: 'Орг',
        field: 'org_price',
      }, {
        name: 'type',
        label: 'Тип',
        field: 'type',
      }, {
        name: 'url',
        label: 'Ссылка',
        field: 'url',
      }, {
        name: 'image',
        label: 'Картинка',
        field: 'image',
      },
    ],
    pagination: {
      rowsPerPage: 0
    },
    goods: []
  }),
  computed: {
    /* goods(){
       return Goods.query().all();
     }*/
  },
  methods: {
    updRow(row, data) {
      if(data.price === ''){
        data.price = null;
      }
      if(data.org_price === ''){
        data.org_price = null;
      }
      Goods.api().post('goods', {
        id: row.id, ...data
      }).then((result) => {
        let idx = this.goods.findIndex((e)=>{
          return e.id==row.id
        });
          this.goods[idx] = result.entities.goods[0];
      });
    },
    getGoods() {
//       Goods.api().get('goods');
      axios.get(path + '/goods').then((res) => {
        this.goods = res.data;
      }).catch((error) => {
        console.error(error);
      });
    }
  },
  created() {
    this.getGoods();
  }
}
</script>

<style scoped>

</style>
