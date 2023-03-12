import { Model } from '@vuex-orm/core'
import {Client, PayersToClients} from "src/store/berries_store/models/index";

export default class Payer extends Model {
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

