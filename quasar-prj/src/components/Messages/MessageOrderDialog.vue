<template>
  <q-dialog>
    <q-card>
      <q-card-section>
        {{ this.message.text }}
      </q-card-section>
      <q-card-section>
        <q-table
          :columns="columns"
          :rows="message_order"
          row-key="id"
        >

          <template v-slot:top>
            <q-btn icon="add" @click="showAddGood"></q-btn>
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
import {MessageOrder} from "src/store/berries_store/models";
import GoodDialog from "components/Messages/GoodDialog.vue";

export default {
  name: "MessageOrderDialog",
  props: {
    message: {},
  },
  emits: ['close'],
  data: () => ({
    good_dialog: false,
    message_order_row: {},
    columns: [{
      name: 'id',
      label: 'id',
      field: 'id'
    }, {
      name: 'good_id',
      label: 'good_id',
      field: row => row.good.id
    }, {
      name: 'good',
      label: 'good',
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
    updRow(row, data) {
      MessageOrder.api().post('message_order', {
        id: row.id, ...data
      });

      console.log(qty);
    },
    async showAddGood() {
      this.message_order_row = {message_id: this.message.id};
      this.good_dialog = true;
    },
    async editGood(item, index) {
      this.message_order_row = item;
      this.good_dialog = true;
    },
    deleteGood(row) {
      console.log("delete " + row);
    },
    getMessageOrder() {
      MessageOrder.api().get('message_order/' + this.message.id, {persistBy: 'create'})
    }
  },
  beforeUpdate() {
    this.getMessageOrder()
    console.log("ok");
  }
}
</script>

<style scoped>
.row-input {
  background: #26A69A;
  justify-content: right;
}
</style>
