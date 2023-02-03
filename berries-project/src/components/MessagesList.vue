<!-- src/components/MessagesList.vue -->
<template>
  <v-container> <!-- Создаем контейнер внутри которого и будут элементы компонента -->

    <v-row class="list__cafes-title"> <!-- В это row выводим заголовок компонента -->
      <v-col>
        <h2 class="text-center text-h3 py-3">List of Messages</h2>
      </v-col>
    </v-row>

    <v-row class="list__cafes-content">
      <v-col md="4" v-for="item in messages" :key="item.id">
        <v-card>

          <v-img
            height="250"
            :src="item.img"
          ></v-img> <!-- С помощью v-img добавляем изображение карточки -->

          <v-card-title>
              <h3 class="text-h4">{{ item.customer.number }}</h3>
              <p>{{ item.customer.push_name }}</p>
          </v-card-title>

          <v-card-text> <!-- Описание заведения -->
            <p class="text-body-1">{{ item.text }}</p>
          </v-card-text>

        </v-card>
      </v-col>
    </v-row>

  </v-container>
</template>
<script>

import axios from 'axios';

export default {
  name: 'MessagesList',
  data: () => ({
    messages: []
  }),
  methods:  {
    getMessages() {
      const path = 'http://localhost:5000/messages';
      axios.get(path).then((res)=>{
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
