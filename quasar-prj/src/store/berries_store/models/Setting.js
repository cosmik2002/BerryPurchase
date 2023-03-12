import { Model } from '@vuex-orm/core'

export default class Setting extends Model {
  static entity = 'settings'
  static primaryKey = 'id'
  static fields () {
    return {
      id: this.attr(null),
      name: this.attr(null),
      value: this.attr(null),
    }
  }
}

