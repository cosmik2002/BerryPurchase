<template>
  <q-dialog @show="show">
    <q-card>
      <q-card-section>
        {{ this.message.text }}
      </q-card-section>
      <q-card-section>
        <q-table
          :columns="columns"
          :rows="message_order"
          wrap-cells
          row-key="id"
        >

          <template v-slot:top>
            <q-btn icon="add" @click="showAddGood"></q-btn>
            <q-btn icon="clear" @click="clearOrder"></q-btn>
          </template>
          <template v-slot:body="props">
            <q-tr :props="props">
              <q-td key="id" :props="props">
                {{ props.row.id }}
              </q-td>
              <q-td key="good_id" :props="props">
                {{ props.row.good.id }}
              </q-td>
              <q-td key="good" :props="props">
                {{ props.row.good.name }}
              </q-td>
              <q-td key="quantity" :props="props">
                <q-input :model-value="props.row.quantity" input-class="row-input"
                         @update:model-value="updRow(props.row, {quantity: $event})"></q-input>
              </q-td>
              <q-td key="price" :props="props">
                <q-input :model-value="props.row.price" input-class="row-input"
                         @update:model-value="updRow(props.row, {price: $event})"></q-input>
              </q-td>
            <q-td key="actions" :props="props">
              <q-btn icon="delete" round @click="deleteGood(props.row, props.rowIndex)"></q-btn>
              <q-btn icon="edit" round @click="editGood(props.row, props.rowIndex)"></q-btn>
            </q-td>
            </q-tr>
          </template>
        </q-table>
      </q-card-section>
      <q-card-actions>
        <q-btn @click="$emit('close')">Закрыть</q-btn>
      </q-card-actions>
    </q-card>
    <good-dialog v-model="good_dialog" :row="message_order_row" @close="good_dialog=false"></good-dialog>
  </q-dialog>
</template>

<script>
import {MessageOrder, Setting} from "src/store/berries_store/models";
import GoodDialog from "components/Messages/GoodDialog.vue";
import axios from "axios";
import {api} from "boot/axios";
const path = process.env.API_URL;
export default {
  name: "MessageOrderDialog",
  props: {
    message: {},
    try_to: {},
  },
  emits: ['close'],
  data: () => ({
    try_to_guess: true,
    good_dialog: false,
    message_order_row: {},
    columns: [/*{
      name: 'id',
      label: 'id',
      field: 'id',
      visible: false
    }, {
      name: 'good_id',
      label: 'good_id',
      field: row => row.good.id
    },*/ {
      name: 'good',
      label: 'good',
      style: 'width: 200px',
      field: row => row.good.name
    }, {
      name: 'quantity',
      label: 'quantity',
      field: 'quantity',
    }, {
      name: 'price',
      label: 'price',
      field: 'price',
    }, {
      name: 'actions',
      label: 'Actions'
    }]
  }),
  components: {
    GoodDialog
  },
  computed: {
    message_order() {
      return MessageOrder.query().with('good').all();
    }
  },
  methods: {
    show (){
      this.try_to_guess = true;
      this.getMessageOrder();
      console.log("show");
    },
    updRow(row, data) {
      MessageOrder.api().post('message_order', {
        id: row.id, ...data
      });

      console.log(qty);
    },
    async showAddGood() {
      this.message_order_row = {message_id: this.message.id, quantity: 1};
      this.good_dialog = true;
    },
    clearOrder(){
      api.get('clear_message_order/'+this.message.id).then((res) => {
        MessageOrder.deleteAll();
      });
      // MessageOrder.api().delete('message_order/' + this.message.id,{delete:})
    },
    async editGood(item, index) {
      this.message_order_row = item;
      this.good_dialog = true;
    },
    deleteGood(row) {
      MessageOrder.api().delete("message_order/" + this.message.id + "/" + row.id, {delete: row.id});
      console.log("delete " + row);
    },
    getMessageOrder() {
      //todo разобраться как запустить по др. точке при открытии диалога
      if (this.try_to_guess){
       this.try_to_guess = false;
        MessageOrder.api().get('message_order_try_to_guess/' + this.message.id, {persistBy: 'create'})
      } else {
        MessageOrder.api().get('message_order/' + this.message.id, {persistBy: 'create'})
      }
    }
  },
  beforeUpdate() {
    // this.getMessageOrder()
  }
}
</script>

<style scoped>
.row-input {
  background: #26A69A;
  justify-content: right;
}
</style>
