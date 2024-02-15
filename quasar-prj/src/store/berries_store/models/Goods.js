import { Model } from '@vuex-orm/core'

export default class Good extends Model {
  static entity = 'goods'
  static primaryKey = 'id'
  static fields () {
    return {
      id: this.attr(null),
      name: this.attr(null),
      variants: this.attr(null),
      price: this.attr(null),
      url: this.attr(null),
      image: this.attr(null),
      org_price: this.attr(null),
      type: this.attr(null),
      active:this.attr(null)
    }
  }
}

