import axios from "axios";
import Payment from "src/store/berries_store/models/Payments";
import Payer from "src/store/berries_store/models/Payer";

export function get_clients({commit}) {
  return axios.get('http://localhost:5000/clients').then((data) => {
         commit('set_clients', data.data);
        }).catch((error) => {
          console.error(error);
        });
}
export function get_payers({commit}) {
  return axios.get('http://localhost:5000/payers').then((data) => {
         // commit('set_payments', data.data);
         data.data.forEach(async (payer) => {
           Payer.insert({data:payer});
         })
        }).catch((error) => {
          console.error(error);
        });
}

export function get_payments({commit}) {
  return axios.get('http://localhost:5000/payments').then((data) => {
         commit('set_payments', data.data);
         data.data.forEach(async (payment) => {
           Payment.insert({data:payment});
         })
        }).catch((error) => {
          console.error(error);
        });
}
export function get_messages({commit}) {
  return axios.get('http://localhost:5000/messages').then((data) => {
         commit('set_messages', data.data);
        }).catch((error) => {
          console.error(error);
        });
}
export function get_goods({commit}) {
  return axios.get('http://localhost:5000/goods').then((data) => {
         commit('set_goods', data.data);
        }).catch((error) => {
          console.error(error);
        });
}
