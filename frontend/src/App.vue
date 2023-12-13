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
    console.log('Backend URL:', process.env.VUE_APP_BACKEND_URL);
    fetch(process.env.VUE_APP_BACKEND_URL)
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
