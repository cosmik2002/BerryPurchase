import { Model } from '@vuex-orm/core'
import {Customer} from "src/store/berries_store/models";
import MessageOrder from "src/store/berries_store/models/MessageOrders";

export default class Message extends Model {
  static entity = 'messages'
    static primaryKey = 'id'
  static fields () {
    return {
      id: this.attr(null),
      wa_id: this.attr(null),
      customer_id: this.attr(null),
      timestamp: this.attr(null),
      text: this.attr(null),
      order_descr: this.attr(null),
      customer: this.belongsTo(Customer, 'customer_id'),
      message_orders: this.hasMany(MessageOrder, 'message_id')
    }
  }
}

