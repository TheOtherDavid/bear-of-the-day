<template>
  <h1>Bear Of The Day!</h1>
  <div>
    <img v-if="imageUrl" :src="imageUrl" class="bear-image">
    <p v-if="metadata">{{ metadata.prompt }}</p>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      imageUrl: null,
      metadata: null
    }
  },
  created() {
    fetch('https://ly8ms91c44.execute-api.us-east-2.amazonaws.com/Prod/bear')
      .then(response => response.json())
      .then(data => {
        this.imageUrl = data.url;
        this.metadata = data.metadata;
      });
  }
}
</script>

<style>
body {
  background-color: #888888;
}
.bear-image {
  width: 40%;
  height: auto;
  border: 10px solid #2c3e50;
}
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
