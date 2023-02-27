import { Model } from '@vuex-orm/core'

export default class PayersToClients extends Model {
  static entity = 'payers_to_clients'

  static primaryKey = ['payer_id', 'client_id']

  static fields () {
    return {
      payer_id: this.attr(null),
      client_id: this.attr(null)
    }
  }
}
