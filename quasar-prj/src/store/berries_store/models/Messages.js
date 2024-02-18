import { Model } from '@vuex-orm/core'
import {Customer, Client} from "src/store/berries_store/models";
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
      props: this.attr(null),
      order_descr: this.attr(null),
      quoted_id: this.attr(null),
      // quoted: this.belongsTo(Message, 'quoted_id'),
      customer: this.belongsTo(Customer, 'customer_id'),
      message_orders: this.hasMany(MessageOrder, 'message_id'),
      for_client_id: this.attr(null),
      for_client: this.belongsTo(Client, 'for_client_id'),
    }
  }
}

