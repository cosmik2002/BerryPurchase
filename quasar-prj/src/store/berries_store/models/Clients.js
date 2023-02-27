import { Model } from '@vuex-orm/core'

export default class Client extends Model {
  static entity = 'clients'
  static fields () {
    return {
      id: this.attr(null),
      name: this.attr(null),
    }
  }
}

