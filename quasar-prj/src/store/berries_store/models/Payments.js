import {Model} from "@vuex-orm/core";
import Payer from "src/store/berries_store/models/Payer";

export default class Payment extends Model {
  // This is the name used as module name of the Vuex Store.
  static entity = 'payments'

  // List of all fields (schema) of the post model. `this.attr` is used
  // for the generic field type. The argument is the default value.
  static fields () {
    return {
      id: this.attr(null),
      sms_id: this.attr(null),
      payer_id: this.attr(null),
      timestamp: this.attr(''),
      sum: this.attr(''),
      operation_code: this.attr(''),
      date_processed: this.attr(''),
      comment: this.attr(''),
      payer: this.belongsTo(Payer, 'payer_id'),
    }
  }
}
