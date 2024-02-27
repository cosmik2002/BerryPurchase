import { Model } from '@vuex-orm/core'

export default class Good extends Model {
  static entity = 'goods'
  static primaryKey = 'id'
  static fields () {
    return {
      id: this.attr(null),
      name: this.attr(null),
      variants: this.attr(null),
      price: this.number(null),
      url: this.attr(null),
      image: this.attr(null),
      org_price: this.number(null),
      type: this.attr(null),
      active: this.attr(null),
      short_name: this.attr(null)
    }
  }
}

