<template>
    <q-item :class="itemClass(item)">
      <q-item-section >
        {{ item.id }}
        <q-item-label v-if="item.payer">
          <div>Плательщик: {{ item.payer.name }}</div>
          <div>Карта: {{ item.payer.card_number }}</div>
        </q-item-label>
        <q-item-label> {{ new Date(item.timestamp).toLocaleDateString() }}
        </q-item-label>
        <q-item-label>
          Сумма: {{ item.sum }} <span v-if="isOst">Остаток: {{item.ost}}</span>
        </q-item-label>
        <q-item-label>
          {{ item.comment }}
        </q-item-label>
      </q-item-section>
      <q-item-section side top>
        <q-item-label v-if="item.payer && item.payer.clients.length > 0">
          <div>Клиент: {{ item.payer.clients[0].name }}</div>
        </q-item-label>
        <q-icon name="more_horiz"
          class="cursor-pointer">
          <q-menu>
            <q-item clickable v-close-popup>
              <q-checkbox
                :model-value="item.not_use || false"
                label="Не&nbsp;учитывать"
                left-label
                @update:model-value="updRow(item, {not_use: $event})"/>
            </q-item>
            <q-item clickable v-close-popup>
              <div @click="$emit('show_payer_to_client_dialog')">Клиент</div>
            </q-item>
          </q-menu>
        </q-icon>
      </q-item-section>
    </q-item>
</template>

<script>
import Payment from "src/store/berries_store/models/Payments";

export default {
  name: "PaymentItem",
  props: ['item', 'isOst'],
  methods: {
    updRow(row, data) {
      let payment = {...this.item};
      payment.not_use = data.not_use || false;
      Payment.api().post('payments/' + this.item.id, payment);
    },
        itemClass(item){
      if(item.not_use)
        return "bg-grey-5";
      if (item.payer && item.payer.clients.length > 0) {
        return "bg-green-1";
      } else {
        return 'bg-red-1';
      }
    },
  }
}
</script>

<style scoped>

</style>
