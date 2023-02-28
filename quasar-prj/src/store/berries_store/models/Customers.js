import { Model } from '@vuex-orm/core'
import {Client, CustomersToClients} from "src/store/berries_store/models/index";

export default class Customer extends Model {
  static entity = 'customers'
  static fields () {
    return {
      id: this.attr(null),
      name: this.attr(null),
      wa_id: this.attr(''),
      number: this.attr(''),
      short_name: this.attr(''),
      push_name: this.attr(''),
      clients: this.belongsToMany(Client, CustomersToClients, 'customer_id', 'client_id')
    }
  }
}

