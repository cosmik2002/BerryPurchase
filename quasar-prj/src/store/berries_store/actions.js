import axios from "axios";

export function get_clients({commit}) {
  return axios.get('http://localhost:5000/clients').then((data) => {
         commit('set_clients', data.data);
        }).catch((error) => {
          console.error(error);
        });
}
export function get_payments({commit}) {
  return axios.get('http://localhost:5000/payments').then((data) => {
         commit('set_payments', data.data);
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
