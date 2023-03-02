import { Model } from '@vuex-orm/core'
import {CustomersToClients, Customer, Payer, PayersToClients} from "src/store/berries_store/models/index";

export default class Client extends Model {
  static entity = 'clients'
  static fields () {
    return {
      id: this.attr(null),
      name: this.attr(null),
      customers: this.belongsToMany(Customer, CustomersToClients, 'client_id', 'customer_id'),
      payers: this.belongsToMany(Payer, PayersToClients, 'client_id', 'payer_id')
    }
  }
}

