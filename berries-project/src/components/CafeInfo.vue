<!-- src/components/Cafe/CafeInfo.vue -->
<template>
  <v-row>

    <v-col md="6">

      <v-card class="h-100">
        <v-img
          height="350"
          :src="main_info.img"
          class="d-flex align-end"
        >
          <!--
            Выше можете заметить что с помощью классов d-flex и align-end, мы прописали CSS свойства display: flex;
            и align-items: flex-end. Это сделает так что название заведения будет выводиться внизу внутри изображения
          -->
          <h2 class="text-h4 ml-4 mb-4 white--text">{{ main_info.title }}</h2>
        </v-img>
      </v-card>

    </v-col>
    <v-col md="6">

       <v-card class="h-100">

         <v-card-text>
          <p class="font-weight-light">{{ main_info.description }}</p>
         </v-card-text>

       </v-card>

    </v-col>

  </v-row>

</template>
<script>
export default {
  name: 'CafeInfo',
  data: () => ({
    main_info: {
      img: 'https://mykaleidoscope.ru/uploads/posts/2020-03/1584281758_61-p-intereri-kafe-i-restoranov-97.jpg',
      title: 'Заголовок заведения',
      description: 'А здесь уже описание заведения'
    }
  })
}
</script>

<style>
.h-100 {
  height: 100%;
}
</style>
