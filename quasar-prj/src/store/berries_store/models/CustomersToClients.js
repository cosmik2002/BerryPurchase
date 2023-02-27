import { Model } from '@vuex-orm/core'

export default class CustomersToClients extends Model {
  static entity = 'customers_to_clients'

  static primaryKey = ['customer_id', 'client_id']

  static fields () {
    return {
      customer_id: this.attr(null),
      client_id: this.attr(null)
    }
  }
}
