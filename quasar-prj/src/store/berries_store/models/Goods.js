import { Model } from '@vuex-orm/core'

export default class Good extends Model {
  static entity = 'goods'
  static fields () {
    return {
      id: this.attr(null),
      name: this.attr(null),
      variants: this.attr(null),
    }
  }
}

