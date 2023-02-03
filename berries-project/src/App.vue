<template>
  <v-card>
    <v-app>
      <v-app-bar title="Application bar"></v-app-bar>

      <v-navigation-drawer>
        <v-list>
          <v-list-item title="Navigation drawer"></v-list-item>
        </v-list>
      </v-navigation-drawer>

      <v-main style="min-height: 300px;">
        <router-view></router-view>
      </v-main>
    </v-app>
  </v-card>
</template>

<script setup>
  //
</script>
