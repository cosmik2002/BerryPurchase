import { store } from 'quasar/wrappers'
import { createStore } from 'vuex'
import berries_store from './berries_store'
import VuexORM from '@vuex-orm/core'
import VuexORMAxios from '@vuex-orm/plugin-axios'
import * as models from './berries_store/models'
import axios from "axios";

/*
 * If not building with SSR mode, you can
 * directly export the Store instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Store instance.
 */
 VuexORM.use(VuexORMAxios, { axios })

// Create a new instance of Database.
const database = new VuexORM.Database()

// Register Models to Database.
  for(var m in models)
    database.register(models[m], {})

export default store(function (/* { ssrContext } */) {
  const Store = createStore({
      plugins: [VuexORM.install(database)],
    modules: {
      berries_store
      // example
    },

    // enable strict mode (adds overhead!)
    // for dev mode and --debug builds only
    strict: process.env.DEBUGGING
  })

  return Store
})
