import { Model } from '@vuex-orm/core'

export default class Customer extends Model {
  static entity = 'customers'
  static fields () {
    return {
      id: this.attr(null),
      name: this.attr(null),
      wa_id: this.attr(''),
      number: this.attr(''),
      short_name: this.attr(''),
      push_name: this.attr('')
    }
  }
}

