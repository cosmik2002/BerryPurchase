<template>
  <q-dialog @show="show">
    <q-card>
      <q-card-section>
       <div>{{ this.message.customer.name ?? this.message.customer.short_name }}</div>
        {{ this.message.text }}
        <q-table
          :columns="columns"
          :rows="message_order"
          wrap-cells
          row-key="id"
          dense
          virtual-scroll
          flat
          style="height: 350px"
                v-model:pagination="pagination"
      :rows-per-page-options="[0]"
        >

          <template v-slot:top>
            <q-btn round size="sm" icon="add" @click="showAddGood"></q-btn>
            &nbsp;
            <q-btn round size="sm" icon="clear" @click="clearOrder"></q-btn>
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
                <q-input dense :model-value="props.row.quantity" input-class="row-input"
                         @update:model-value="updRow(props.row, {quantity: $event})"></q-input>
              </q-td>
<!--              <q-td key="price" :props="props">
                {{props.row.good.price ? parseInt(props.row.good.price) : ''}}
              </q-td>-->
            <q-td key="actions" :props="props">
              <q-btn icon="delete" round size="sm"
                     @click="deleteGood(props.row, props.rowIndex)"></q-btn>
            &nbsp;
              <q-btn icon="edit" round size="sm"
                     @click="editGood(props.row, props.rowIndex)"></q-btn>
            </q-td>
            </q-tr>
          </template>
        </q-table>
      </q-card-section>
      <q-card-section>
        <q-input
          debounce="1000"
          :model-value="comment"
          type="textarea"
          autogrow
          @update:model-value="updComment($event)"/>
      </q-card-section>
      <q-card-actions>
        <q-btn @click="$emit('close')">Закрыть</q-btn>
      </q-card-actions>
    </q-card>
    <good-dialog v-model="good_dialog" :good="message_order_row.good" @close="good_dialog=false"></good-dialog>
    <add-good-dialog v-model="add_good_dialog" :row="message_order_row" @close="add_good_dialog=false"></add-good-dialog>
  </q-dialog>
</template>

<script>
import {Message, MessageOrder, Setting} from "src/store/berries_store/models";
import GoodDialog from "components/Messages/GoodDialog.vue";
import AddGoodDialog from "components/Messages/AddGoodDialog.vue";
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
    add_good_dialog: false,
    message_order_row: {},
    comment: '',
    pagination:{
      rowsPerPage:0
    },
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
      label: 'Название',
      style: 'width: 40%',
      align: 'left',
      field: row => row.good.name
    }, {
      name: 'quantity',
      style: 'width: 20%',
      label: 'Кол-во',
      field: 'quantity',
      align: 'left',
    },/* {
      name: 'price',
      label: 'Цена',
      field: 'price',
    },*/ {
      name: 'actions',
      label: 'Действия'
    }]
  }),
  components: {
    GoodDialog,
    AddGoodDialog
  },
  computed: {
    message_order() {
      return MessageOrder.query().with('good').all();
    }
  },
  methods: {
    show (){
      this.try_to_guess = false;
      this.getMessageOrder();
      console.log("show");
    },
    updComment(event) {
      let msg = {...this.message};
      msg.props = msg.props ? {...msg.props, comment: event} : { comment: event};
      Message.api().post('messages/' + this.message.id, msg);
    },
    updRow(row, data) {
      MessageOrder.api().post('message_order', {
        id: row.id, ...data
      });
    },
    async showAddGood() {
      this.message_order_row = {message_id: this.message.id, quantity: 1};
      this.add_good_dialog = true;
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
      if (!this.message.order_descr){
       // this.try_to_guess = false;
        MessageOrder.api().get('message_order_try_to_guess/' + this.message.id, {persistBy: 'create'})
      } else {
        MessageOrder.api().get('message_order/' + this.message.id, {persistBy: 'create'})
      }
        this.comment = this.message.props.comment;

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
