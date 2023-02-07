<!-- src/components/MessagesList.vue -->
<template>
  <v-container> <!-- Создаем контейнер внутри которого и будут элементы компонента -->

    <v-row class="list__cafes-title"> <!-- В это row выводим заголовок компонента -->
      <v-col>
        <h2 class="text-center text-h3 py-3">List of Messages</h2>
      </v-col>
    </v-row>

  <v-list>
    <v-list-item v-for="item in messages"
    :key="item.id"
    :title="item.customer.number +' ~~ '+ item.customer.push_name"
    :subtitle="item.text"
     @click.stop="messageClick(item.wa_id)">
    </v-list-item>
  </v-list>
  </v-container>
    <v-dialog v-model="dialog" scrollable max-width="30%">
      <v-card>
        <v-card-title>Title</v-card-title>
        <v-divider></v-divider>
  <v-card-text>
        <v-combobox
          :label="title"
        v-model="client"
        :items="clients"
        item-title="name">
        </v-combobox>
    </v-card-text>
      </v-card>
    </v-dialog>
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
    loaded: false
  }),
  methods:  {
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
