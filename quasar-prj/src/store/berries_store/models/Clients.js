import { Model } from '@vuex-orm/core'

export default class Client extends Model {
  static entity = 'clients'
    static primaryKey = 'id'
  static fields () {
    return {
      id: this.attr(null),
      name: this.attr(null),
      customers: this.attr(null),
      payers: this.attr(null),
    }
  }
}


