import {Model} from '@vuex-orm/core'
import Good from "src/store/berries_store/models/Goods";

export default class MessageOrder extends Model {
  static entity = 'message_orders'
  static primaryKey = 'id'
  static fields() {
    return {
      id: this.attr(null),
      message_id: this.attr(null),
      good_id: this.attr(null),
      quantity: this.attr(null),
      price: this.attr(null),
      good: this.belongsTo(Good, 'good_id'),
    }
  }
}

