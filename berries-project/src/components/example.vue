<template>
  <v-app >
    <example-dialog @userInfo="getUserData($event)"></example-dialog>
  </v-app>
</template>

<script>
import ExampleDialog from '@/components/ExampleDialog.vue'


export default {
  name: 'example',
  components:{
    ExampleDialog
  },

  data () {
    return{

    }
  },
  methods:{
    getUserData(value){
      console.log(value)
    }
  }
};
</script>
