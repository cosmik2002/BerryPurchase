<template>
  <q-dialog>
    <q-card>
      <q-table
        :rows="itog.data" @row-click="itogDialogClick"></q-table>
      {{ itog.customer.name }}
      <q-input v-if="sendBtn"
        debounce="1000"
        :model-value="send_text"
        type="textarea"
        autogrow/>
      <q-card-actions>
        <q-btn @click="$emit('close')">Close</q-btn>
        <q-btn v-if="sendBtn" @click="send()">Send</q-btn>
      </q-card-actions>
    </q-card>
      <message-order-dialog v-model="message_order_dialog" :message="message" @close="message_order_dialog=false"/>
  </q-dialog>
</template>

<script>
import {Message} from "src/store/berries_store/models";
import MessageOrderDialog from "components/Messages/MessageOrderDialog.vue";

export default {
  name: "itogDialog",
  components: {MessageOrderDialog},
  props: {
    itog: {
      type: Object,
      default: function () {
        return {}
      },
    },
    sendBtn: {
      type: Boolean,
      default: false
    }
  },
  data: function () {
    return {
      send_text: '',
      message_order_dialog: false,
      message: {}
    };
  },
  methods: {
    send(a, b, c) {
      axios.post(path + "/send", {customer: this.itog.customer.id, text: this.send_text});
    },

    async itogDialogClick(event, row) {
      await Message.api().get('messages/' + row.id, {
        persistBy: 'create',
        persistOptions: {
          insertOrUpdate: ['customer', 'clients']
        }
      });
      this.message = Message.query().where('id', row.id).with('for_client').with('customer').with('customer.clients').get()[0];
      this.message_order_dialog = true;
    },
  }
}
</script>

<style scoped>

</style>
