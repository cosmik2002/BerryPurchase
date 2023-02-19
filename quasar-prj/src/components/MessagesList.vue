<template>
  <q-btn @click="loadMessages()">Load Messages</q-btn>
  <div>{{ result }}</div>
  <q-list>
    <q-item v-for="item in messages"
                 :key="item.id" v-ripple:red>
      <q-item-section>
        <q-item-label>{{ item.customer.number }}~~{{ item.customer.push_name}} </q-item-label>
        <q-item-label>{{ item.text }}</q-item-label>
      </q-item-section>

    </q-item>
  </q-list>
</template>
<script>

import axios from 'axios';
const path = 'http://localhost:5000';

export default {
  name: 'MessagesList',
  data: () => ({
    messages: [],
    clients: [],
    client: [],
    dialog: false,
    title: 'null',
    loaded: false,
    result: {}
  }),
  methods:  {
    loadMessages() {
        axios.get(path+'/load_messages').then((res) => {
          this.result = res.data;
        }).catch((error) => {
          console.error(error);
        });

    },
    messageClick(id){
      this.title = id;
      if (!this.loaded) {
        this.loaded = true;
        axios.get(path+'/clients').then((res) => {
          this.clients = res.data;
          this.dialog = true;
        }).catch((error) => {
          console.error(error);
        });
      } else {
        this.dialog = true;
      }
    },
    getMessages() {
      // const path = 'http://localhost:5000/messages';
      axios.get(path+'/messages').then((res)=>{
        this.messages = res.data;
      }).catch((error) => {
        console.error(error);
      });
    }
  },
  created() {
    this.getMessages();
  }
}
</script>
