<template>
  <q-table
    :columns="columns"
    :rows="goods"
    wrap-cells
    virtual-scroll
    style="max-height: 90vh"
    :visible-columns = "visColumns()"
    v-model:pagination="pagination"
    :rows-per-page-options="[0]"
    :filter="filter"
  >
          <template v-slot:body="props">
            <q-tr :props="props">
              <q-td v-for="col in columns"
                    :key="col.name"
                    :props="props">
               <span v-if="col.name==='name'">
                <a v-if= "props.row['url']" :href="props.row['url']" target="_blank">{{ props.row[col.name] }}</a>
                 <div v-else>{{ props.row[col.name] }}</div>
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
                <span v-else-if="col.name==='weight'">
                   <q-input
                     dense
                     debounce="1000"
                     :model-value="props.row[col.name] ? parseFloat(props.row[col.name]) : ''"
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
                <span v-else-if="col.name==='actions'">
                          <q-icon name="more_horiz"
          class="cursor-pointer">
          <q-menu>
            <q-item clickable v-close-popup icon="delete"
                     @click="deleteGood(props.row, props.rowIndex)">
             <q-item-section avatar si>
              <q-icon name="delete"></q-icon>
               </q-item-section>
              <q-item-section>Удалить</q-item-section>
            </q-item>
            <q-item clickable v-close-popup
                     @click="editGood(props.row, props.rowIndex)">
             <q-item-section avatar si>
              <q-icon name="edit"></q-icon>
               </q-item-section>
              <q-item-section>Редактировать</q-item-section>
            </q-item>
          </q-menu>
        </q-icon>
                </span>
                <span v-else>{{ props.row[col.name] }}</span>
              </q-td>
            </q-tr>
          </template>
          <template v-slot:top-right>
        <q-input borderless dense debounce="300" v-model="filter" placeholder="Search">
          <template v-slot:append>
            <q-icon name="search" />
          </template>
        </q-input>
      </template>
  </q-table>
    <good-dialog v-model="good_dialog" :good="good" @close="good_dialog=false"></good-dialog>

</template>

<script>
import {Goods, MessageOrder} from
    "src/store/berries_store/models";
import axios from "axios";
import GoodDialog from "components/Messages/GoodDialog.vue";

const path = process.env.API_URL;

export default {
  name: "GoodsPage",
  components: {GoodDialog},
  data: () => ({
    pr: null,
    good_dialog: false,
    good: {},
    filter: '',
    columns: [
      {
        name: 'name',
        label: 'Название',
        // style: 'max-width: 10%',
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
        name: 'weight',
        label: 'Вес',
        field: 'weight',
      }, {
        name: 'actions',
        label: 'Действия',
      },
    ],
    pagination: {
      rowsPerPage: 0
    },
    // goods: []
  }),
  computed: {
     goods(){
       return Goods.query().all();
     }
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
    visColumns() {
      const cols = [];
      const xsHidCols = ['variants', 'org_price', 'price', 'type', 'active'];
      for(let i in this.columns ) {
        if (!this.$q.screen.xs || xsHidCols.indexOf(this.columns[i].name) === -1) {
        cols.push(this.columns[i].name);
      }
      }
      return cols
    },
    async editGood(item, index) {
      this.good = item;
      this.good_dialog = true;
    },
    deleteGood(row) {
      Goods.api().delete("goods/" + row.id, {delete: row.id});
    },
    getGoods() {
      Goods.api().get('goods');
      // axios.get(path + '/goods').then((res) => {
      //   this.goods = res.data;
      // }).catch((error) => {
      //   console.error(error);
      // });
    }
  },
  created() {
    this.getGoods();
  }
}
</script>

<style scoped>

</style>
