import { Model } from '@vuex-orm/core'
import {PayersToClients, CustomersToClients, Payer, Customer} from "src/store/berries_store/models/index";

export default class Client extends Model {
  static entity = 'clients'
    static primaryKey = 'id'
  static fields () {
    return {
      id: this.attr(null),
      name: this.attr(null),
      customers: this.belongsToMany(Customer, CustomersToClients, 'client_id', 'customer_id'),
      payers: this.belongsToMany(Payer, PayersToClients, 'client_id', 'payer_id')
    }
  }
}

/*
export class Payer extends Model {
  static entity = 'payers'
  static primaryKey = 'id'
  static fields () {
    return {
      id: this.attr(null),
      name: this.attr(null),
      card_number: this.attr(''),
      comments: this.attr(''),
      clients: this.belongsToMany(Client, PayersToClients, 'payer_id', 'client_id')
    }
  }
}

export class Customer extends Model {
  static entity = 'customers'
    static primaryKey = 'id'
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
*/


